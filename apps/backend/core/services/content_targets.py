from articles.models import PublishedArticle
from core.models import ContentTarget


def get_or_create_published_article_target(published_article: PublishedArticle):
    return ContentTarget.objects.get_or_create(
        target_type=ContentTarget.TargetType.PUBLISHED_ARTICLE,
        published_article=published_article,
        defaults={"comment": None},
    )[0]


def get_or_create_comment_target(comment):
    return ContentTarget.objects.get_or_create(
        target_type=ContentTarget.TargetType.COMMENT,
        comment=comment,
        defaults={"published_article": None},
    )[0]

