from django.utils import timezone

from core.models import ContentTarget
from core.utils.markdown import render_markdown_mentions

from .models import BaseReport, ContentReport, UserReport


TERMINAL_REPORT_STATUSES = {
    BaseReport.ReportStatus.RESOLVED,
    BaseReport.ReportStatus.REJECTED,
}


def build_content_report_snapshot(target: ContentTarget):
    snapshot = {
        "content_target_id": str(target.id),
        "target_type": target.target_type,
        "target_type_display": target.get_target_type_display(),
    }

    if target.target_type == ContentTarget.TargetType.PUBLISHED_ARTICLE:
        article = target.published_article
        snapshot.update(
            {
                "target_object_id": str(article.id),
                "title": article.title,
                "source_article_id": str(article.source_article_id),
                "author_id": str(article.source_article.author_id) if article.source_article.author_id else None,
                "html": article.html,
                "publication_at": article.publication_at.isoformat(),
            }
        )
        return snapshot

    if target.target_type == ContentTarget.TargetType.COMMENT:
        comment = target.comment
        snapshot.update(
            {
                "target_object_id": str(comment.id),
                "author_id": str(comment.author_id) if comment.author_id else None,
                "body": comment.body,
                "render_body": render_markdown_mentions(comment.body, comment.mentions),
                "mentions": comment.mentions,
                "parent_id": str(comment.parent_id) if comment.parent_id else None,
                "is_deleted": comment.is_deleted,
            }
        )
        return snapshot

    if target.target_type == ContentTarget.TargetType.COMMUNITY_POST:
        post = target.community_post
        snapshot.update(
            {
                "target_object_id": str(post.id),
                "author_id": str(post.author_id) if post.author_id else None,
                "body": post.body,
                "render_body": render_markdown_mentions(post.body, post.mentions),
                "mentions": post.mentions,
                "is_deleted": post.is_deleted,
            }
        )
        return snapshot

    return snapshot


def build_user_report_snapshot(user):
    avatar_url = user.avatar.url if user.avatar else None
    return {
        "reported_user_id": str(user.id),
        "username": user.username,
        "avatar_url": avatar_url,
        "signature": user.signature,
        "is_active": user.is_active,
        "is_moderator": user.is_moderator,
        "date_joined": user.date_joined.isoformat(),
    }


def create_content_report(*, reporter, target: ContentTarget, reason: int, description: str = ""):
    snapshot = build_content_report_snapshot(target)
    return ContentReport.objects.create(
        reporter=reporter,
        target=target,
        target_type=target.target_type,
        target_object_id=snapshot["target_object_id"],
        reason=reason,
        description=description,
        snapshot=snapshot,
    )


def create_user_report(*, reporter, reported_user, reason: int, description: str = ""):
    snapshot = build_user_report_snapshot(reported_user)
    return UserReport.objects.create(
        reporter=reporter,
        reported_user=reported_user,
        reported_user_id_snapshot=reported_user.id,
        reason=reason,
        description=description,
        snapshot=snapshot,
    )


def moderate_report(*, report, moderator, status: int, resolution_note: str = ""):
    report.status = status
    report.resolution_note = resolution_note

    if status in TERMINAL_REPORT_STATUSES:
        report.resolved_by = moderator
        report.resolved_at = timezone.now()
        report.save(update_fields=["status", "resolution_note", "resolved_by", "resolved_at", "updated_at"])
    else:
        report.resolved_by = None
        report.resolved_at = None
        report.save(update_fields=["status", "resolution_note", "resolved_by", "resolved_at", "updated_at"])

    return report
