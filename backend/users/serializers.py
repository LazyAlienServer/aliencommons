from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

import random
import io
from PIL import Image

from core.validators import (
    FileSizeValidator,
    FileTypeValidator,
    PasswordValidator,
)
from core.serializers import BaseModelSerializer

User = get_user_model()


class ProfileCreateSerializer(BaseModelSerializer):
    """
    Register a new user.
    """
    username = serializers.CharField(
        required=True,
        error_messages={
            'required': "A username is required",
        },
        validators = [
            UniqueValidator(queryset=User.objects.all(), message="This username has already existed")
        ],
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': "An email is required",
        },
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="This email has already existed")
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

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                detail="Passwords do not match", code='passwords_do_not_match'
            )

        return data

    def create(self, validated_data):
        def pick_random_avatar():
            avatar = random.choice(settings.DEFAULT_AVATARS)
            return avatar

        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            avatar=pick_random_avatar(),
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class ProfileListSerializer(BaseModelSerializer):
    """
    List all user profiles
    """
    id = serializers.IntegerField(read_only=True)
    avatar = serializers.ImageField(read_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'avatar', 'username', 'signature')
        read_only_fields = ('id', 'avatar', 'username', 'signature')


class ProfileRetrieveSerializer(BaseModelSerializer):
    """
    Retrieve one user profile.
    """
    id = serializers.IntegerField(read_only=True)
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


class ProfileUpdateSerializer(BaseModelSerializer):
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


class CustomLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        access_lifetime = api_settings.ACCESS_TOKEN_LIFETIME
        refresh_lifetime = api_settings.REFRESH_TOKEN_LIFETIME
        data['access_token_lifetime'] = str(access_lifetime.total_seconds())
        data['refresh_token_lifetime'] = str(refresh_lifetime.days)

        return data


class CustomLoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except ObjectDoesNotExist:
            raise AuthenticationFailed(
                self.error_messages.get("no_active_account", "No active account"),
                code="no_active_account",
            )

        access_lifetime = api_settings.ACCESS_TOKEN_LIFETIME
        data["access_token_lifetime"] = str(access_lifetime.total_seconds())

        return data
