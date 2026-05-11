from rest_framework import routers

from .views import CommunityPostViewSet


router = routers.SimpleRouter()
router.register(r"community_posts", CommunityPostViewSet, basename="community_posts")

urlpatterns = router.urls
