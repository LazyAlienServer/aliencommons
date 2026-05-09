from rest_framework import routers

from .views import CommentViewSet


router = routers.SimpleRouter()
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = []
urlpatterns += router.urls

