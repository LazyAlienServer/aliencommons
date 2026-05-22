from django.db import transaction
from django.utils import timezone

from datetime import timedelta
import json
import hashlib

from articles.models import SourceArticle, PublishedArticle, ArticleSnapshot, ArticleEvent
from core.exceptions import ServiceError
from core.utils.alienmark import render_md_to_html
from logs.logging import get_logger
from notifications.services import notify_subscribed_author_posted
from .markdown import extract_title_from_markdown, validate_article_markdown

logger = get_logger(__name__)


def _get_locked_source_article(source_article_id):
    """
    Return a locked SourceArticle for business logic.
    If the SourceArticle does not exist, a ServiceError will be raised.
    """
    try:
        source_article = SourceArticle.objects.select_for_update().get(id=source_article_id)
        return source_article

    except SourceArticle.DoesNotExist:
        raise ServiceError(
            detail="Source article not found", code='source_article_not_found'
        )


@transaction.atomic
def save_draft(*, source_article_id, actor, title=None, markdown=None):
    source_article = _get_locked_source_article(source_article_id)
    workflow = ArticleWorkflow(source_article=source_article, actor=actor)
    return workflow.save_draft(title=title, markdown=markdown)


@transaction.atomic
def submit(*, source_article_id, actor):
    source_article = _get_locked_source_article(source_article_id)
    workflow = ArticleWorkflow(source_article=source_article, actor=actor)
    return workflow.submit()


@transaction.atomic
def withdraw(*, source_article_id, actor):
    source_article = _get_locked_source_article(source_article_id)
    workflow = ArticleWorkflow(source_article=source_article, actor=actor)
    return workflow.withdraw()


@transaction.atomic
def approve(*, source_article_id, actor):
    source_article = _get_locked_source_article(source_article_id)
    workflow = ArticleWorkflow(source_article=source_article, actor=actor)
    return workflow.approve()


@transaction.atomic
def reject(*, source_article_id, actor):
    source_article = _get_locked_source_article(source_article_id)
    workflow = ArticleWorkflow(source_article=source_article, actor=actor)
    return workflow.reject()


@transaction.atomic
def unpublish(*, source_article_id, actor):
    source_article = _get_locked_source_article(source_article_id)
    workflow = ArticleWorkflow(source_article=source_article, actor=actor)
    return workflow.unpublish()


@transaction.atomic
def soft_delete(*, source_article_id, actor):
    source_article = _get_locked_source_article(source_article_id)
    workflow = ArticleWorkflow(source_article=source_article, actor=actor)
    return workflow.soft_delete()


class ArticleWorkflow:
    def __init__(self, *, source_article, actor):
        self.source_article = source_article
        self.article_snapshot = self._get_last_snapshot()
        self.actor = actor

    def _get_last_snapshot(self):
        """
        Return the most recent snapshot of the source article.
        'None' will be returned if no snapshot is available.
        """
        return (
            ArticleSnapshot.objects
            .filter(source_article=self.source_article)
            .order_by('-created_at')
            .first()
        )

    @staticmethod
    def _hash_and_normalize(title, markdown):
        """
        Make a stable representation of the article and calculate its hash value.
        It strips the spaces before and after the title and the summary.
        Return: hash_value
        """
        items_to_hash = {'title': title.strip(), 'markdown': markdown}
        items_json = json.dumps(items_to_hash, sort_keys=True)
        hash_value = hashlib.blake2b(items_json.encode("utf-8")).hexdigest()

        return hash_value

    def _get_the_published_article(self) -> PublishedArticle:
        """
        Return the published version of the article
        """
        return PublishedArticle.objects.filter(source_article=self.source_article).first()

    @staticmethod
    def _assert(*, condition, error_message):
        """
        Check whether the source article's status is legal.
        """
        if not condition:
            raise ServiceError(detail=error_message, code='state_transition_error')

    @staticmethod
    def _within_submit_cooldown(last_moderation_at, hours=12):
        """
        Check if the source article is within the submit cooldown.
        Return is_within
        """
        if not last_moderation_at:  # First time submit
            return False

        now = timezone.now()
        is_within = now - last_moderation_at < timedelta(hours=hours)

        return is_within

    def _create_or_update_published_article(self) -> PublishedArticle:
        """
        Create or update the source article's published version.
        Return the published_article.
        """
        published_article = self._get_the_published_article()
        html = render_md_to_html(self.article_snapshot.markdown)

        if published_article:
            published_article.title = self.article_snapshot.title
            published_article.html = html
            published_article.publication_at = timezone.now()
            published_article.save(update_fields=['title', 'html', 'publication_at'])

            return published_article

        published_article = PublishedArticle.objects.create(
            source_article=self.source_article,
            title=self.article_snapshot.title,
            html=html,
            publication_at=timezone.now(),
        )
        notify_subscribed_author_posted(
            actor=self.source_article.author,
            target=published_article.content_target,
            content_kind="published_article",
        )

        return published_article

    def _create_article_event(self, event_type: ArticleEvent.EventType) -> ArticleEvent:
        """
        Return an article event.
        """
        return ArticleEvent.objects.create(
            source_article=self.source_article,
            article_snapshot=self.article_snapshot,
            event_type=event_type,
            actor=self.actor,
        )

    @staticmethod
    def _build_action_result(event: ArticleEvent):
        """
        Build and log a standard action result.
        Return a dict containing the information.
        """
        event_type: ArticleEvent.EventType = ArticleEvent.EventType(event.event_type)
        actor_id = event.actor_id
        source_article_id = event.source_article_id
        article_snapshot_id = event.article_snapshot_id if event.article_snapshot else None
        event_id = event.id

        logger.info(
            f"Article {event_type.label} action completed",
            extra={
                'event_type': event_type,
                'actor_id': actor_id,
                'source_article_id': source_article_id,
                'article_snapshot_id': article_snapshot_id,
                'event_id': event_id,
            }
        )

        return {
            "event_type": event_type,
            "actor_id": actor_id,
            "source_article_id": source_article_id,
            "article_snapshot_id": article_snapshot_id,
            "event_id": event_id,
        }

    def save_draft(self, *, title=None, markdown=None):
        """
        Save editable article content.

        Only drafts and unpublished articles may be edited. A previously
        unpublished article becomes a draft again when new source content is
        saved, so it can enter the submission flow normally.
        """
        self._assert(
            condition=self.source_article.status in (
                SourceArticle.ArticleStatus.DRAFT,
                SourceArticle.ArticleStatus.UNPUBLISHED,
            ),
            error_message="Only draft or unpublished articles can be edited."
        )

        has_changed = False

        if markdown is not None and markdown != self.source_article.markdown:
            title = extract_title_from_markdown(
                markdown,
                max_length=SourceArticle._meta.get_field("title").max_length,
            )
            self.source_article.markdown = markdown
            self.source_article.title = title
            has_changed = True

        update_fields = []
        if has_changed:
            self.source_article.version += 1
            self.source_article.last_saved_at = timezone.now()
            update_fields.extend(["title", "markdown", "version", "last_saved_at"])

        if self.source_article.status == SourceArticle.ArticleStatus.UNPUBLISHED:
            self.source_article.status = SourceArticle.ArticleStatus.DRAFT
            update_fields.append("status")

        if update_fields:
            self.source_article.save(update_fields=update_fields)

        return self.source_article

    def submit(self):
        validate_article_markdown(
            self.source_article.markdown,
            max_length=SourceArticle._meta.get_field("title").max_length,
        )

        last_moderation_at = self.source_article.last_moderation_at
        if last_moderation_at and self._within_submit_cooldown(last_moderation_at, hours=6):
            raise ServiceError(
                detail="Submission has a cooldown of 6 hours.",
                code='cooldown_error'
            )

        self._assert(
            condition=self.source_article.status == SourceArticle.ArticleStatus.DRAFT,
            error_message="You can only submit an article draft!"
        )

        current_hash = self._hash_and_normalize(
            self.source_article.title,
            self.source_article.markdown
        )

        if self.article_snapshot and self.article_snapshot.hash == current_hash:
            raise ServiceError(
                detail="Please modify before submission.",
                code='no_change_error'
            )

        new_snapshot = ArticleSnapshot.objects.create(
            source_article=self.source_article,
            title=self.source_article.title,
            markdown=self.source_article.markdown,
            hash=current_hash,
            source_version=self.source_article.version,
            moderation_status=ArticleSnapshot.SnapshotStatus.PENDING
        )
        self.article_snapshot = new_snapshot

        self.source_article.status = SourceArticle.ArticleStatus.PENDING
        self.source_article.save(update_fields=['status'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.SUBMIT)

        return self._build_action_result(event=article_event)

    def withdraw(self):
        self._assert(
            condition=self.source_article.status == SourceArticle.ArticleStatus.PENDING,
            error_message="You can only withdraw a pending article!"
        )

        if not self.article_snapshot:
            raise ServiceError(
                detail="A article snapshot is required!",
                code='article_snapshot_required'
            )

        self.source_article.status = SourceArticle.ArticleStatus.DRAFT
        self.source_article.save(update_fields=['status'])

        self.article_snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.WITHDRAWN
        self.article_snapshot.save(update_fields=['moderation_status'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.WITHDRAW)

        return self._build_action_result(event=article_event)

    def approve(self):
        self._assert(
            condition=self.source_article.status == SourceArticle.ArticleStatus.PENDING,
            error_message="You can only approve a pending article!"
        )

        if not self.article_snapshot:
            raise ServiceError(
                detail="There are no snapshots for this article!",
                code='no_snapshot_error'
            )

        self._create_or_update_published_article()

        self.source_article.status = SourceArticle.ArticleStatus.PUBLISHED
        self.source_article.last_moderation_at = timezone.now()
        self.source_article.save(update_fields=['status', 'last_moderation_at'])

        self.article_snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.APPROVED
        self.article_snapshot.save(update_fields=['moderation_status'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.APPROVE)

        return self._build_action_result(event=article_event)

    def reject(self):
        self._assert(
            condition=self.source_article.status == SourceArticle.ArticleStatus.PENDING,
            error_message="You can only reject a pending article!"
        )

        if not self.article_snapshot:
            raise ServiceError(
                detail="There are no snapshots for this article!",
                code='no_snapshot_error'
            )

        self.source_article.status = SourceArticle.ArticleStatus.DRAFT
        self.source_article.last_moderation_at = timezone.now()
        self.source_article.save(update_fields=['status', 'last_moderation_at'])

        self.article_snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.REJECTED
        self.article_snapshot.save(update_fields=['moderation_status'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.REJECT)

        return self._build_action_result(event=article_event)

    def unpublish(self):
        self._assert(
            condition=self.source_article.status == SourceArticle.ArticleStatus.PUBLISHED,
            error_message="You can only unpublish a published article!"
        )

        if not self.article_snapshot:
            raise ServiceError(
                detail="There are no snapshots for this article!",
                code='no_snapshot_error'
            )

        self.source_article.status = SourceArticle.ArticleStatus.UNPUBLISHED
        self.source_article.last_moderation_at = timezone.now()
        self.source_article.save(update_fields=['status', 'last_moderation_at'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.UNPUBLISH)

        return self._build_action_result(event=article_event)

    def soft_delete(self):
        """
        For this method, snapshot may not be available
        as user may delete an article that has never been submitted.
        """
        self._assert(
            condition=self.source_article.status != SourceArticle.ArticleStatus.PENDING,
            error_message="A pending article cannot be deleted! Please withdraw it first."
        )

        published_article = self._get_the_published_article()

        if published_article:
            published_article.delete()

        self.source_article.is_deleted = True  # Soft delete source article
        self.source_article.save(update_fields=['is_deleted'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.DELETE)

        return self._build_action_result(event=article_event)
