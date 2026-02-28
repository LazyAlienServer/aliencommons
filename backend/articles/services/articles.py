from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import get_object_or_404

from uuid import UUID
from typing import TypedDict, Any

from articles.models import (
    SourceArticle, PublishedArticle, ArticleSnapshot, ArticleEvent
)
from core.exceptions import ServiceError
from .utils import (
    hash_and_normalize, get_last_snapshot, get_published_version, within_submit_cooldown
)

User = get_user_model()


def get_locked_source_article(source_article_id: UUID) -> SourceArticle:
    article = get_object_or_404(
        SourceArticle.objects.select_for_update(),
        pk=source_article_id,
    )

    return article


def create_or_update_published_article(*,
                                       source_article: SourceArticle,
                                       article_snapshot: ArticleSnapshot) -> PublishedArticle:

    published = get_published_version(source_article)

    if published:
        published.title = article_snapshot.title
        published.content = article_snapshot.content
        published.save(update_fields=['title', 'content'])

        return published

    published_article = PublishedArticle.objects.create(
        source_article=source_article,
        title=article_snapshot.title,
        content=article_snapshot.content,
    )

    return published_article


class ArticleActionResult(TypedDict):
    event_type: int
    actor_id: int
    source_article_id: UUID | Any
    status: int
    snapshot_id: UUID | None | Any
    event_id: UUID | Any


def build_article_action_result(*,
                                source_article: SourceArticle,
                                actor: User,
                                event: ArticleEvent,
                                article_snapshot: ArticleSnapshot) -> ArticleActionResult:

    return {
        "event_type": event.event_type,
        "actor_id": actor.id,
        "source_article_id": source_article.id,
        "status": source_article.status,
        "snapshot_id": article_snapshot.id if article_snapshot else None,
        "event_id": event.id,
    }


@transaction.atomic
def submit(*,
           source_article_id: UUID,
           actor: User,
           annotation: str | None = None) -> ArticleActionResult:

    source_article = get_locked_source_article(source_article_id)

    # If submitted within 12 hours since last submission, raise CoolingDownError
    last_moderation_at = source_article.last_moderation_at
    if last_moderation_at and within_submit_cooldown(last_moderation_at, hours=6):
        raise ServiceError(
            detail="Submission has a cooldown of 6 hours.",
            code='cooldown_error'
        )

    if source_article.status == SourceArticle.ArticleStatus.PENDING:
        raise ServiceError(
            detail="You cannot submit a pending article!",
            code='state_transition_error'
        )

    current_hash = hash_and_normalize(
        source_article.title,
        source_article.content
    )

    # If unchanged, raise NoChangeError
    last_snapshot = get_last_snapshot(source_article)
    if last_snapshot and last_snapshot.content_hash == current_hash:
        raise ServiceError(
            detail="Please modify before submission.",
            code='no_change_error'
        )

    # Create snapshot
    snapshot = ArticleSnapshot.objects.create(
        article=source_article,
        title=source_article.title,
        content=source_article.content,
        content_hash=current_hash,
        moderation_status=ArticleSnapshot.SnapshotStatus.PENDING
    )

    # Create article event
    article_event = ArticleEvent.objects.create(
        source_article=source_article,
        article_snapshot=snapshot,
        annotation=annotation,
        event_type=ArticleEvent.EventType.SUBMIT,
        actor=actor,
    )

    # Update source article
    source_article.status = SourceArticle.ArticleStatus.PENDING
    source_article.save(update_fields=['status'])

    return build_article_action_result(
        source_article=source_article, actor=actor, event=article_event, article_snapshot=snapshot
    )


@transaction.atomic
def withdraw(*,
             source_article_id: UUID,
             actor: User,
             annotation: str | None = None) -> ArticleActionResult:

    source_article = get_locked_source_article(source_article_id)

    if source_article.status != SourceArticle.ArticleStatus.PENDING:
        raise ServiceError(
            detail="You can only withdraw a pending article!",
            code='state_transition_error'
        )

    snapshot = get_last_snapshot(source_article)

    # Create article event
    article_event = ArticleEvent.objects.create(
        source_article=source_article,
        article_snapshot=snapshot,
        annotation=annotation,
        event_type=ArticleEvent.EventType.WITHDRAW,
        actor=actor,
    )

    # Update source article
    source_article.status = SourceArticle.ArticleStatus.DRAFT
    source_article.save(update_fields=['status'])

    # Update last article snapshot
    snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.WITHDRAWN
    snapshot.save(update_fields=['moderation_status'])

    return build_article_action_result(
        source_article=source_article, actor=actor, event=article_event, article_snapshot=snapshot
    )


@transaction.atomic
def approve(*,
            source_article_id: UUID,
            actor: User,
            annotation: str | None = None) -> ArticleActionResult:

    source_article = get_locked_source_article(source_article_id)

    # Can only approve when the Source Article is PENDING
    if source_article.status != SourceArticle.ArticleStatus.PENDING:
        raise ServiceError(
            detail="Only a pending article can be approved!",
            code='state_transition_error'
        )

    snapshot = get_last_snapshot(source_article)
    if not snapshot:
        raise ServiceError(
            detail="There are no snapshots for this article!",
            code='no_change_error'
        )

    create_or_update_published_article(
        source_article=source_article, article_snapshot=snapshot
    )

    # Create article event
    article_event = ArticleEvent.objects.create(
        source_article=source_article,
        article_snapshot=snapshot,
        annotation=annotation,
        event_type=ArticleEvent.EventType.APPROVE,
        actor=actor,
    )

    # Update source article
    source_article.status = SourceArticle.ArticleStatus.PUBLISHED
    source_article.last_moderation_at = timezone.now()
    source_article.save(update_fields=['status', 'last_moderation_at'])

    # Update last article snapshot
    snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.APPROVED
    snapshot.save(update_fields=['moderation_status'])

    return build_article_action_result(
        source_article=source_article, actor=actor, event=article_event, article_snapshot=snapshot
    )


@transaction.atomic
def reject(*,
           source_article_id: UUID,
           actor: User,
           annotation: str | None = None) -> ArticleActionResult:

    source_article = get_locked_source_article(source_article_id)

    # Can only reject when the Source Article is PENDING
    if source_article.status != SourceArticle.ArticleStatus.PENDING:
        raise ServiceError(
            detail="Only a pending article can be rejected!",
            code='state_transition_error'
        )

    snapshot = get_last_snapshot(source_article)
    if not snapshot:
        raise ServiceError(
            detail="There are no snapshots for this article!",
            code='no_snapshot_error'
        )

    # Create article event
    article_event = ArticleEvent.objects.create(
        source_article=source_article,
        article_snapshot=snapshot,
        annotation=annotation,
        event_type=ArticleEvent.EventType.REJECT,
        actor=actor,
    )

    # Update source article
    source_article.status = SourceArticle.ArticleStatus.REJECTED
    source_article.last_moderation_at = timezone.now()
    source_article.save(update_fields=['status', 'last_moderation_at'])

    # Update last article snapshot
    snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.REJECTED
    snapshot.save(update_fields=['moderation_status'])

    return build_article_action_result(
        source_article=source_article, actor=actor, event=article_event, article_snapshot=snapshot
    )


@transaction.atomic
def unpublish(*,
              source_article_id: UUID,
              actor: User,
              annotation: str | None = None) -> ArticleActionResult:

    source_article = get_locked_source_article(source_article_id)

    # Can only unpublish when the Source Article is PUBLISHED
    if source_article.status != SourceArticle.ArticleStatus.PUBLISHED:
        raise ServiceError(
            detail="Only a published article can be unpublished!",
            code='state_transition_error'
        )

    snapshot = get_last_snapshot(source_article)
    if not snapshot:
        raise ServiceError(
            detail="There are no snapshots for this article!",
            code='no_snapshot_error'
        )

    # Create article event
    article_event = ArticleEvent.objects.create(
        source_article=source_article,
        article_snapshot=snapshot,
        annotation=annotation,
        event_type=ArticleEvent.EventType.UNPUBLISH,
        actor=actor,
    )

    # Update source article
    source_article.status = SourceArticle.ArticleStatus.UNPUBLISHED
    source_article.last_moderation_at = timezone.now()
    source_article.save(update_fields=['status', 'last_moderation_at'])

    return build_article_action_result(
        source_article=source_article, actor=actor, event=article_event, article_snapshot=snapshot
    )


@transaction.atomic
def soft_delete(*,
                source_article_id: UUID,
                actor: User,
                annotation: str | None = None) -> ArticleActionResult:

    source_article = get_locked_source_article(source_article_id)

    # Can only delete when the Source Article is not PENDING
    if source_article.status == SourceArticle.ArticleStatus.PENDING:
        raise ServiceError(
            detail="A pending article cannot be deleted! Please withdraw it from moderation first.",
            code='state_transition_error'
        )

    # For this method, snapshot may not be available
    # as user may delete an article that has never been submitted.
    # In this case, 'None' will be returned.
    snapshot = get_last_snapshot(source_article)

    published_article = get_published_version(source_article)

    # Soft delete source article
    source_article.delete()

    # Delete associated published article
    if published_article:
        published_article.delete()

    # Create article event
    article_event = ArticleEvent.objects.create(
        source_article=source_article,
        article_snapshot=snapshot,
        annotation=annotation,
        event_type=ArticleEvent.EventType.DELETE,
        actor=actor,
    )

    # Update Source Article
    source_article.status = SourceArticle.ArticleStatus.DELETED
    source_article.save(update_fields=['status'])

    return build_article_action_result(
        source_article=source_article, actor=actor, event=article_event, article_snapshot=snapshot
    )
