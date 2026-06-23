from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from drf_std_response import EnvelopeMixin
from ..serializers import EmailVerifyRequestSerializer, EmailVerifyResponseSerializer
from ..services.users import verify_email


class EmailViewSet(EnvelopeMixin, viewsets.ViewSet):
    """
    A viewset that collects endpoints which relate to email models.
    """
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def verify_email(self, request):
        input_serializer = EmailVerifyRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = verify_email(
            user=request.user,
            email=input_serializer.validated_data['email'],
            code=input_serializer.validated_data['code'],
        )

        output_serializer = EmailVerifyResponseSerializer(instance=result)

        return self.format_success_response(
            message="email verified successfully",
            code='email_verified',
            data=output_serializer.data,
            status_code=status.HTTP_200_OK
        )
