from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import ContentTarget

from .models import BaseReport, ContentReport, UserReport


User = get_user_model()


class BaseReportReadSerializer(serializers.ModelSerializer):
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)


class ContentReportReadSerializer(BaseReportReadSerializer):
    target_type_display = serializers.CharField(source="target.get_target_type_display", read_only=True)

    class Meta:
        model = ContentReport
        fields = (
            "id",
            "reporter",
            "target",
            "target_type",
            "target_type_display",
            "target_object_id",
            "reason",
            "reason_display",
            "description",
            "snapshot",
            "status",
            "status_display",
            "resolution_note",
            "resolved_by",
            "resolved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class UserReportReadSerializer(BaseReportReadSerializer):
    class Meta:
        model = UserReport
        fields = (
            "id",
            "reporter",
            "reported_user",
            "reported_user_id_snapshot",
            "reason",
            "reason_display",
            "description",
            "snapshot",
            "status",
            "status_display",
            "resolution_note",
            "resolved_by",
            "resolved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ContentReportWriteSerializer(serializers.Serializer):
    target = serializers.UUIDField()
    reason = serializers.ChoiceField(choices=BaseReport.ReportReason.choices)
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_target(self, value):
        try:
            return ContentTarget.objects.select_related(
                "published_article",
                "published_article__source_article",
                "comment",
                "comment__author",
                "comment__parent",
            ).get(pk=value)
        except ContentTarget.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Content target does not exist",
                code="content_target_not_found",
            ) from exc


class UserReportWriteSerializer(serializers.Serializer):
    reported_user = serializers.UUIDField()
    reason = serializers.ChoiceField(choices=BaseReport.ReportReason.choices)
    description = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_reported_user(self, value):
        try:
            return User.objects.get(pk=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError(
                detail="Reported user does not exist",
                code="reported_user_not_found",
            ) from exc

    def validate(self, attrs):
        request = self.context["request"]
        if attrs["reported_user"].id == request.user.id:
            raise serializers.ValidationError(
                detail="Users cannot report themselves",
                code="self_report_not_allowed",
            )
        return attrs


class ReportModerationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=BaseReport.ReportStatus.choices)
    resolution_note = serializers.CharField(required=False, allow_blank=True, default="")

