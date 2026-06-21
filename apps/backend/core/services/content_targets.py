from articles.models import ArticlePublication
from core.models import ContentTarget


def get_or_create_article_publication_target(article_publication: ArticlePublication):
    return ContentTarget.objects.get_or_create(
        target_type=ContentTarget.TargetType.ARTICLE_PUBLICATION,
        article_publication=article_publication,
        defaults={"comment": None, "community_post": None},
    )[0]


def get_or_create_comment_target(comment):
    return ContentTarget.objects.get_or_create(
        target_type=ContentTarget.TargetType.COMMENT,
        comment=comment,
        defaults={"article_publication": None, "community_post": None},
    )[0]


def get_or_create_community_post_target(community_post):
    return ContentTarget.objects.get_or_create(
        target_type=ContentTarget.TargetType.COMMUNITY_POST,
        community_post=community_post,
        defaults={"article_publication": None, "comment": None},
    )[0]
