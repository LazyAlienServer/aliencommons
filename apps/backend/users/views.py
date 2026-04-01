from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.views.mixins import (
    FormattedResponseMixin, MyListModelMixin, MyRetrieveModelMixin
)
from .services.users import register, verify_email
from .serializers import (
    UserRegisterInputSerializer,
    UserRegisterOutputSerializer,
    UserListSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    CustomLoginSerializer,
    CustomLoginRefreshSerializer,
    EmailVerifyInputSerializer,
    EmailVerifyOutputSerializer
)


User = get_user_model()


class UserViewSet(MyListModelMixin,
                  MyRetrieveModelMixin,
                  FormattedResponseMixin,
                  viewsets.GenericViewSet):
    """
    A viewset that collects 4 API endpoints which relates to user module.

    Register, User List, User Info, Update (username, signature, avatar)
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


class AuthViewSet(FormattedResponseMixin, viewsets.ViewSet):
    """
    A viewset that collects 2 API endpoints which relates to user module.

    Login, Refresh Login Token
    """
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = CustomLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.format_success_response(
            message="user login successfully",
            code="user_login",
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh_login_token(self, request):
        serializer = CustomLoginRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.format_success_response(
            message="login token refreshed successfully",
            code="token_refreshed",
            data=serializer.validated_data,
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
