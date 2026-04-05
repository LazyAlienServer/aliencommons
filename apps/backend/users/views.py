from django.contrib.auth import get_user_model, authenticate, login, logout

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import AuthenticationFailed

from core.views.mixins import (
    FormattedResponseMixin, MyListModelMixin, MyRetrieveModelMixin
)
from .services.users import register, verify_email
from .services.sessions import create_user_session, delete_user_session
from .serializers import (
    UserRegisterInputSerializer,
    UserRegisterOutputSerializer,
    UserListSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    UserLoginSerializer,
    EmailVerifyInputSerializer,
    EmailVerifyOutputSerializer
)


User = get_user_model()


class UserViewSet(MyListModelMixin,
                  MyRetrieveModelMixin,
                  FormattedResponseMixin,
                  viewsets.GenericViewSet):
    """
    A viewset that collects API endpoints which relates to User.
    """
    queryset = User.objects.order_by("-date_joined")
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    default_serializer_class = UserRetrieveSerializer

    serializer_class_mapping = {
        'list': UserListSerializer,
        'retrieve': UserRetrieveSerializer,
        'create': UserRegisterOutputSerializer,
    }

    def get_serializer_class(self):
        self.action: str
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def get_permissions(self):
        self.action: str
        if self.action in ('create', 'list', 'retrieve'):
            self.permission_classes = [AllowAny]
        elif self.action in ('me',):
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def create(self, request):
        input_serializer = UserRegisterInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = register(
            username=input_serializer.validated_data['username'],
            email=input_serializer.validated_data['email'],
            password=input_serializer.validated_data['password'],
        )

        output_serializer = UserRegisterOutputSerializer(instance=result)

        return self.format_success_response(
            message="user registered successfully",
            code="user_registered",
            data=output_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserRetrieveSerializer(user)

            return self.format_success_response(
                message="my profile retrieved",
                code='my_profile_retrieved',
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.format_success_response(
            message="my profile updated",
            code='my_profile_updated',
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class SessionViewSet(FormattedResponseMixin, viewsets.ViewSet):
    """
    A viewset that collects API endpoints which relates to UserSession.

    Note that login() and logout(), provided by django.contrib.auth,
    manages Django built-in Session object;
    Meanwhile, create_user_session() and delete_user_session(), provided by services,
    manages UserSession object.
    """
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
        create_user_session(request, user)

        return self.format_success_response(
            message="user login successfully",
            code="user_login",
            data=None,
            status_code=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        delete_user_session(request)

        return self.format_success_response(
            message="user logout successfully",
            code="user_logout",
            data=None,
            status_code=status.HTTP_200_OK
        )


class EmailViewSet(FormattedResponseMixin, viewsets.ViewSet):
    """
    A viewset that collects 1 API endpoint which relates to email model.
    """
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def verify_email(self, request):
        input_serializer = EmailVerifyInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = verify_email(
            user=request.user,
            email=input_serializer.validated_data['email'],
            code=input_serializer.validated_data['code'],
        )

        output_serializer = EmailVerifyOutputSerializer(instance=result)

        return self.format_success_response(
            message="email verified successfully",
            code='email_verified',
            data=output_serializer.data,
            status_code=status.HTTP_200_OK
        )
