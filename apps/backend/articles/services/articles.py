from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from datetime import timedelta
import json
import hashlib

from articles.models import (
    Article,
    ArticleSource,
    ArticlePublication,
    ArticlePublicationVersion,
    ArticleSnapshot,
    ArticleEvent,
)
from drf_std_response import ServiceError
from core.utils.alienmark import render_md_to_html
from logs.logging import get_logger
from notifications.services import notify_subscribed_author_posted
from .markdown import extract_title_from_markdown, validate_article_markdown

logger = get_logger(__name__)


def _get_locked_article(article_id):
    """
    Return a locked Article for business logic.
    If the Article does not exist, a ServiceError will be raised.
    """
    try:
        article = Article.objects.select_for_update().select_related("source", "author").get(id=article_id)
        return article

    except Article.DoesNotExist:
        raise ServiceError(
            detail="Article not found", code='article_not_found'
        )


@transaction.atomic
def create_article(*, actor, markdown=None):
    markdown = markdown if markdown is not None else str(ArticleSource.default_markdown)
    title = extract_title_from_markdown(
        markdown,
        max_length=ArticleSource._meta.get_field("title").max_length,
    )
    article = Article.objects.create(author=actor)
    ArticleSource.objects.create(
        article=article,
        title=title,
        markdown=markdown,
    )
    ArticleEvent.objects.create(
        article=article,
        article_snapshot=None,
        event_type=ArticleEvent.EventType.CREATE,
        actor=actor,
    )
    return article


@transaction.atomic
def save_draft(*, article_id, actor, title=None, markdown=None):
    article = _get_locked_article(article_id)
    workflow = ArticleWorkflow(article=article, actor=actor)
    return workflow.save_draft(title=title, markdown=markdown)


@transaction.atomic
def submit(*, article_id, actor):
    article = _get_locked_article(article_id)
    workflow = ArticleWorkflow(article=article, actor=actor)
    return workflow.submit()


@transaction.atomic
def withdraw(*, article_id, actor):
    article = _get_locked_article(article_id)
    workflow = ArticleWorkflow(article=article, actor=actor)
    return workflow.withdraw()


@transaction.atomic
def approve(*, article_id, actor):
    article = _get_locked_article(article_id)
    workflow = ArticleWorkflow(article=article, actor=actor)
    return workflow.approve()


@transaction.atomic
def reject(*, article_id, actor):
    article = _get_locked_article(article_id)
    workflow = ArticleWorkflow(article=article, actor=actor)
    return workflow.reject()


@transaction.atomic
def unpublish(*, article_id, actor):
    article = _get_locked_article(article_id)
    workflow = ArticleWorkflow(article=article, actor=actor)
    return workflow.unpublish()


@transaction.atomic
def soft_delete(*, article_id, actor):
    article = _get_locked_article(article_id)
    workflow = ArticleWorkflow(article=article, actor=actor)
    return workflow.soft_delete()


class ArticleWorkflow:
    def __init__(self, *, article, actor):
        self.article = article
        self.article_source = article.source
        self.article_snapshot = self._get_last_snapshot()
        self.actor = actor

    def _get_last_snapshot(self):
        """
        Return the most recent snapshot of the article.
        'None' will be returned if no snapshot is available.
        """
        return (
            ArticleSnapshot.objects
            .filter(article=self.article)
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

    def _get_the_publication(self) -> ArticlePublication:
        """
        Return the current publication of the article
        """
        return ArticlePublication.objects.filter(article=self.article).first()

    @staticmethod
    def _assert(*, condition, error_message):
        """
        Check whether the article's status is legal.
        """
        if not condition:
            raise ServiceError(detail=error_message, code='state_transition_error')

    @staticmethod
    def _within_submit_cooldown(last_moderation_at, hours=12):
        """
        Check if the article is within the submit cooldown.
        Return is_within
        """
        if not last_moderation_at:  # First time submit
            return False

        now = timezone.now()
        is_within = now - last_moderation_at < timedelta(hours=hours)

        return is_within

    def _create_publication_version(self) -> ArticlePublicationVersion:
        """
        Create the next public version from the approved snapshot.
        Return the article publication version.
        """
        article_publication = self._get_the_publication()
        publication_at = timezone.now()
        html = render_md_to_html(self.article_snapshot.markdown)

        article_publication, created = ArticlePublication.objects.get_or_create(
            article=self.article,
            defaults={"published_at": publication_at},
        )
        next_version = (
            article_publication.versions.aggregate(max_version=Max("version"))["max_version"] or 0
        ) + 1

        article_publication_version = ArticlePublicationVersion.objects.create(
            publication=article_publication,
            approved_snapshot=self.article_snapshot,
            version=next_version,
            title=self.article_snapshot.title,
            html=html,
            publication_at=publication_at,
        )

        if created:
            notify_subscribed_author_posted(
                actor=self.article.author,
                target=article_publication.content_target,
                content_kind="article_publication",
            )

        return article_publication_version

    def _create_article_event(self, event_type: ArticleEvent.EventType) -> ArticleEvent:
        """
        Return an article event.
        """
        return ArticleEvent.objects.create(
            article=self.article,
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
        article_id = event.article_id
        article_snapshot_id = event.article_snapshot_id if event.article_snapshot else None
        event_id = event.id

        logger.info(
            f"Article {event_type.label} action completed",
            extra={
                'event_type': event_type,
                'actor_id': actor_id,
                'article_id': article_id,
                'article_snapshot_id': article_snapshot_id,
                'event_id': event_id,
            }
        )

        return {
            "event_type": event_type,
            "actor_id": actor_id,
            "article_id": article_id,
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
            condition=self.article.status in (
                Article.ArticleStatus.DRAFT,
                Article.ArticleStatus.UNPUBLISHED,
            ),
            error_message="Only draft or unpublished articles can be edited."
        )

        has_changed = False

        if markdown is not None and markdown != self.article_source.markdown:
            title = extract_title_from_markdown(
                markdown,
                max_length=ArticleSource._meta.get_field("title").max_length,
            )
            self.article_source.markdown = markdown
            self.article_source.title = title
            has_changed = True

        source_update_fields = []
        article_update_fields = []
        if has_changed:
            self.article_source.version += 1
            self.article.last_saved_at = timezone.now()
            source_update_fields.extend(["title", "markdown", "version", "updated_at"])
            article_update_fields.append("last_saved_at")

        if self.article.status == Article.ArticleStatus.UNPUBLISHED:
            self.article.status = Article.ArticleStatus.DRAFT
            article_update_fields.append("status")

        if source_update_fields:
            self.article_source.save(update_fields=source_update_fields)
        if article_update_fields:
            self.article.save(update_fields=article_update_fields)

        return self.article

    def submit(self):
        validate_article_markdown(
            self.article_source.markdown,
            max_length=ArticleSource._meta.get_field("title").max_length,
        )

        last_moderation_at = self.article.last_moderation_at
        if last_moderation_at and self._within_submit_cooldown(last_moderation_at, hours=6):
            raise ServiceError(
                detail="Submission has a cooldown of 6 hours.",
                code='cooldown_error'
            )

        self._assert(
            condition=self.article.status == Article.ArticleStatus.DRAFT,
            error_message="You can only submit an article draft!"
        )

        current_hash = self._hash_and_normalize(
            self.article_source.title,
            self.article_source.markdown
        )

        if self.article_snapshot and self.article_snapshot.hash == current_hash:
            raise ServiceError(
                detail="Please modify before submission.",
                code='no_change_error'
            )

        new_snapshot = ArticleSnapshot.objects.create(
            article=self.article,
            title=self.article_source.title,
            markdown=self.article_source.markdown,
            hash=current_hash,
            source_version=self.article_source.version,
            moderation_status=ArticleSnapshot.SnapshotStatus.PENDING
        )
        self.article_snapshot = new_snapshot

        self.article.status = Article.ArticleStatus.PENDING
        self.article.save(update_fields=['status'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.SUBMIT)

        return self._build_action_result(event=article_event)

    def withdraw(self):
        self._assert(
            condition=self.article.status == Article.ArticleStatus.PENDING,
            error_message="You can only withdraw a pending article!"
        )

        if not self.article_snapshot:
            raise ServiceError(
                detail="An article snapshot is required!",
                code='article_snapshot_required'
            )

        self.article.status = Article.ArticleStatus.DRAFT
        self.article.save(update_fields=['status'])

        self.article_snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.WITHDRAWN
        self.article_snapshot.save(update_fields=['moderation_status'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.WITHDRAW)

        return self._build_action_result(event=article_event)

    def approve(self):
        self._assert(
            condition=self.article.status == Article.ArticleStatus.PENDING,
            error_message="You can only approve a pending article!"
        )

        if not self.article_snapshot:
            raise ServiceError(
                detail="There are no snapshots for this article!",
                code='no_snapshot_error'
            )

        self.article_snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.APPROVED
        self.article_snapshot.save(update_fields=['moderation_status'])

        self._create_publication_version()

        self.article.status = Article.ArticleStatus.PUBLISHED
        self.article.last_moderation_at = timezone.now()
        self.article.save(update_fields=['status', 'last_moderation_at'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.APPROVE)

        return self._build_action_result(event=article_event)

    def reject(self):
        self._assert(
            condition=self.article.status == Article.ArticleStatus.PENDING,
            error_message="You can only reject a pending article!"
        )

        if not self.article_snapshot:
            raise ServiceError(
                detail="There are no snapshots for this article!",
                code='no_snapshot_error'
            )

        self.article.status = Article.ArticleStatus.DRAFT
        self.article.last_moderation_at = timezone.now()
        self.article.save(update_fields=['status', 'last_moderation_at'])

        self.article_snapshot.moderation_status = ArticleSnapshot.SnapshotStatus.REJECTED
        self.article_snapshot.save(update_fields=['moderation_status'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.REJECT)

        return self._build_action_result(event=article_event)

    def unpublish(self):
        self._assert(
            condition=self.article.status == Article.ArticleStatus.PUBLISHED,
            error_message="You can only unpublish a published article!"
        )

        if not self.article_snapshot:
            raise ServiceError(
                detail="There are no snapshots for this article!",
                code='no_snapshot_error'
            )

        article_publication = self._get_the_publication()
        if article_publication:
            article_publication.delete()

        self.article.status = Article.ArticleStatus.UNPUBLISHED
        self.article.last_moderation_at = timezone.now()
        self.article.save(update_fields=['status', 'last_moderation_at'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.UNPUBLISH)

        return self._build_action_result(event=article_event)

    def soft_delete(self):
        """
        For this method, snapshot may not be available
        as user may delete an article that has never been submitted.
        """
        self._assert(
            condition=self.article.status != Article.ArticleStatus.PENDING,
            error_message="A pending article cannot be deleted! Please withdraw it first."
        )

        article_publication = self._get_the_publication()

        if article_publication:
            article_publication.delete()

        self.article.is_deleted = True
        self.article.save(update_fields=['is_deleted'])

        article_event = self._create_article_event(event_type=ArticleEvent.EventType.DELETE)

        return self._build_action_result(event=article_event)
