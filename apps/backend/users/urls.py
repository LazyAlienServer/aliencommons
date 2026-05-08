from rest_framework.routers import DefaultRouter

from .views import EmailViewSet, SessionViewSet, UserSubscriptionViewSet, UserViewSet


router = DefaultRouter()
router.register(r'profiles', UserViewSet, basename='profile')
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'emails', EmailViewSet, basename='email')
router.register(r'subscriptions', UserSubscriptionViewSet, basename='subscription')

urlpatterns = router.urls
