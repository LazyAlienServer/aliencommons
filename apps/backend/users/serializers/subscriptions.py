from rest_framework import serializers

from ..models import UserSubscription


class UserSubscriptionReadSerializer(serializers.ModelSerializer):
    subscriber_username = serializers.CharField(source="subscriber.username", read_only=True)
    subscribed_to_username = serializers.CharField(source="subscribed_to.username", read_only=True)

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "subscriber",
            "subscriber_username",
            "subscribed_to",
            "subscribed_to_username",
            "created_at",
        )
        read_only_fields = fields


class UserSubscriptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ("subscribed_to",)
        validators = []

    def validate_subscribed_to(self, value):
        subscriber = self.context["request"].user

        if value.id == subscriber.id:
            raise serializers.ValidationError(
                detail="You cannot subscribe to yourself",
                code="self_subscription",
            )

        existing = UserSubscription.objects.filter(
            subscriber=subscriber,
            subscribed_to=value,
        )
        if self.instance is not None:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError(
                detail="You already subscribed to this user",
                code="duplicate_subscription",
            )

        return value
