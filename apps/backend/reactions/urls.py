from rest_framework import routers

from .views import ReactionViewSet


router = routers.SimpleRouter()
router.register(r"reactions", ReactionViewSet, basename="reaction")

urlpatterns = []
urlpatterns += router.urls

