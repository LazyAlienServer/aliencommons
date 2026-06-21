from rest_framework import routers

from .views import (
    ArticleViewSet,
    ArticlePublicationViewSet,
    ArticleSnapshotViewSet,
    ArticleEventReadViewset,
    CollectionViewSet,
    CollectionItemViewSet,
)


router = routers.SimpleRouter()

router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'article_publications', ArticlePublicationViewSet, basename='article_publication')
router.register(r'article_snapshots', ArticleSnapshotViewSet, basename='article_snapshot')
router.register(r'article_events', ArticleEventReadViewset, basename='article_event')
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'collection_items', CollectionItemViewSet, basename='collection_item')

urlpatterns = []

urlpatterns += router.urls
