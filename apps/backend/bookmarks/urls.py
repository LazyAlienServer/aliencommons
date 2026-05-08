from rest_framework.routers import DefaultRouter

from .views import BookmarkFolderViewSet, BookmarkViewSet


router = DefaultRouter()
router.register(r"bookmark_folders", BookmarkFolderViewSet, basename="bookmark_folder")
router.register(r"bookmarks", BookmarkViewSet, basename="bookmark")

urlpatterns = router.urls
