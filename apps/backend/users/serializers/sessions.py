from rest_framework import serializers

from ..utils import normalize_email


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': "An email is required",
        },
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'required': "A password is required",
        },
    )

    def validate_email(self, value):
        """
        Return a normalized email.
        """
        return normalize_email(value)
