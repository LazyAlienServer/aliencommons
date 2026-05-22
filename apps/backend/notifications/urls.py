from rest_framework import routers

from .views import NotificationDeliveryViewSet


router = routers.SimpleRouter()
router.register(r"notifications", NotificationDeliveryViewSet, basename="notification")

urlpatterns = []
urlpatterns += router.urls

