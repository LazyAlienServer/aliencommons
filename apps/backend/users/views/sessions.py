from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated

from drf_std_response import EnvelopeMixin
from ..serializers import UserLoginSerializer
from ..services.sessions import create_user_session, delete_user_session


class SessionViewSet(EnvelopeMixin, viewsets.ViewSet):
    """
    A viewset that collects API endpoints which relates to UserSession.

    Note that login() and logout(), provided by django.contrib.auth,
    manages Django built-in Session object;
    Meanwhile, create_user_session() and delete_user_session(), provided by services,
    manages UserSession object.
    """
    def get_permissions(self):
        self.action: str
        if self.action in ("login",):
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request, email=serializer.validated_data['email'], password=serializer.validated_data['password']
        )
        if user is None:
            raise AuthenticationFailed("Invalid credentials")

        login(request, user)
        request.session[settings.SESSION_EXPIRY_REFRESH_FIELD] = timezone.now().isoformat()
        create_user_session(request, user)

        return self.format_success_response(
            message="user login successfully",
            code="user_login",
            data=None,
            status_code=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        delete_user_session(request)
        logout(request)

        return self.format_success_response(
            message="user logout successfully",
            code="user_logout",
            data=None,
            status_code=status.HTTP_200_OK
        )
