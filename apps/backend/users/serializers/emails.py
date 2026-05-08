from django.core.validators import RegexValidator

from rest_framework import serializers

from ..utils import normalize_email


class EmailVerifyInputSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': "An email is required",
        },
    )
    code = serializers.CharField(
        required=True,
        trim_whitespace=True,
        error_messages={
            'required': "A verification code is required",
        },
        validators=[
            RegexValidator(
                regex=r"^\d{6}$",
                message="Verification code must be a 6-digit number"
            )
        ]
    )

    def validate_email(self, value):
        """
        Return a normalized email.
        """
        return normalize_email(value)


class EmailVerifyOutputSerializer(serializers.Serializer):
    """
    Serialize the verified email address.
    """
    email = serializers.EmailField(read_only=True)
