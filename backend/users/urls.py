from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, UserViewSet, EmailViewSet


router = DefaultRouter()
router.register(r'profiles', UserViewSet, basename='profile')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'emails', EmailViewSet, basename='email')

urlpatterns = router.urls
