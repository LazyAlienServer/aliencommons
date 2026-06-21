from django.db.models.signals import post_save
from django.dispatch import receiver

from core.services.content_targets import (
    get_or_create_article_publication_target,
    get_or_create_comment_target,
    get_or_create_community_post_target,
)


@receiver(post_save, sender="articles.ArticlePublication")
def create_article_publication_content_target(sender, instance, created, **kwargs):
    if created:
        get_or_create_article_publication_target(instance)


@receiver(post_save, sender="comments.Comment")
def create_comment_content_target(sender, instance, created, **kwargs):
    if created:
        get_or_create_comment_target(instance)


@receiver(post_save, sender="posts.CommunityPost")
def create_community_post_content_target(sender, instance, created, **kwargs):
    if created:
        get_or_create_community_post_target(instance)
