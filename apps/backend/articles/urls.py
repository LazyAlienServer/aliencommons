from rest_framework import routers

from .views import (
    SourceArticleViewSet,
    PublishedArticleViewSet,
    ArticleSnapshotViewSet,
    ArticleEventReadViewset,
    CollectionViewSet,
    CollectionItemViewSet,
)


router = routers.SimpleRouter()

router.register(r'source_articles', SourceArticleViewSet, basename='source_article')
router.register(r'published_articles', PublishedArticleViewSet, basename='published_article')
router.register(r'article_snapshots', ArticleSnapshotViewSet, basename='article_snapshot')
router.register(r'article_events', ArticleEventReadViewset, basename='article_event')
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'collection_items', CollectionItemViewSet, basename='collection_item')

urlpatterns = []

urlpatterns += router.urls
