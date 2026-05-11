from rest_framework import routers

from .views import NotificationViewSet


router = routers.SimpleRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = []
urlpatterns += router.urls
