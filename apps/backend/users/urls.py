from rest_framework.routers import DefaultRouter

from .views import SessionViewSet, UserViewSet, EmailViewSet


router = DefaultRouter()
router.register(r'profiles', UserViewSet, basename='profile')
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'emails', EmailViewSet, basename='email')

urlpatterns = router.urls
