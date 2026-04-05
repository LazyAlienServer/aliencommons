from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import AuthenticationFailed
import io
from PIL import Image

from core.validators import (
    FileSizeValidator,
    FileTypeValidator,
    PasswordValidator,
)
from .models import EmailAddress
from .utils import normalize_email

User = get_user_model()


class UserRegisterInputSerializer(serializers.Serializer):
    """
    Register a new user.
    """
    username = serializers.CharField(
        required=True,
        error_messages={
            'required': "A username is required",
        },
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="This username has already existed")
        ],
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': "An email is required",
        },
        validators=[
            UniqueValidator(queryset=EmailAddress.objects.all(), message="This email has already existed")
        ],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'required': "A password is required",
        },
        validators=[PasswordValidator()],
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'required': "A confirm password is required",
        }
    )

    def validate_email(self, value):
        """
        Normalize email and check its uniqueness.
        Return a normalized email.
        """
        email = normalize_email(value)

        # Email uniqueness is both checked here and in field validation,
        # given that there are two email forms: not normalized and normalized
        if EmailAddress.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                detail="This email is already in use", code="email_taken",
            )

        return email

    def validate(self, data):
        """
        Check if password equals to confirm_password.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                detail="Passwords do not match", code='passwords_do_not_match'
            )

        return data


class UserRegisterOutputSerializer(serializers.Serializer):
    """
    Return the result of user registration.
    """
    user_id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    email_verified = serializers.BooleanField(read_only=True)
    resend_cooldown_seconds = serializers.IntegerField(read_only=True)
    code_ttl_seconds = serializers.IntegerField(read_only=True)


class UserListSerializer(serializers.ModelSerializer):
    """
    List all user profiles
    """
    id = serializers.UUIDField(read_only=True)
    avatar = serializers.ImageField(read_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'avatar', 'username', 'signature')
        read_only_fields = ('id', 'avatar', 'username', 'signature')


class UserRetrieveSerializer(serializers.ModelSerializer):
    """
    Retrieve one user profile.
    """
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    avatar = serializers.ImageField(read_only=True)
    signature = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_moderator = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'avatar', 'signature', 'username', 'is_moderator', 'date_joined',
        )
        read_only_fields = (
            'id', 'email', 'avatar', 'signature', 'username', 'is_moderator', 'date_joined',
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Update a user profile.
    Only Username, Signature, Avatar are supported.
    """
    username = serializers.CharField(
        max_length=20,
        min_length=3,
        error_messages={
            'max_length': 'The username must be less than 20 characters',
            'min_length': 'The username must be at least 3 characters',
        },
        validators=[
            UniqueValidator(queryset=User.objects.all(), message='The username has already existed', ),
        ],
    )

    avatar = serializers.ImageField(
        validators=[
            FileSizeValidator(object_display_name="avatar", max_size_mb=2),
            FileTypeValidator(object_display_name="avatar")
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'avatar')

    def update(self, instance, validated_data):
        username = validated_data.get('username', None)
        if username is not None:
            setattr(instance, 'username', username)

        signature = validated_data.get('signature', None)
        if signature is not None:
            setattr(instance, 'signature', signature)

        avatar = validated_data.get('avatar', None)
        if avatar is not None:
            image = Image.open(avatar)
            image = image.convert("RGB")
            image.thumbnail((512, 512))
            buffer = io.BytesIO()
            image.save(buffer, format="WEBP", quality=85)
            webp_file = ContentFile(buffer.getvalue())

            instance.avatar.save(f"{instance.pk}_avatar.webp", webp_file, save=False)

        instance.save()

        return instance


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
