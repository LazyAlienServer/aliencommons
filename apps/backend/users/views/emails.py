from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.views.mixins import FormattedResponseMixin
from ..serializers import EmailVerifyInputSerializer, EmailVerifyOutputSerializer
from ..services.users import verify_email


class EmailViewSet(FormattedResponseMixin, viewsets.ViewSet):
    """
    A viewset that collects endpoints which relate to email models.
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
