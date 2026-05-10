from django.contrib import admin

from .models import ContentReport, UserReport


class BaseReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reporter",
        "reason",
        "status",
        "resolved_by",
        "resolved_at",
        "created_at",
    )
    list_filter = (
        "reason",
        "status",
        "created_at",
        ("reporter", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("description", "resolution_note")
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "reporter",
        "description",
        "snapshot",
        "created_at",
        "updated_at",
    )


@admin.register(ContentReport)
class ContentReportAdmin(BaseReportAdmin):
    readonly_fields = BaseReportAdmin.readonly_fields + (
        "target",
        "target_type",
        "target_object_id",
    )


@admin.register(UserReport)
class UserReportAdmin(BaseReportAdmin):
    readonly_fields = BaseReportAdmin.readonly_fields + (
        "reported_user",
        "reported_user_id_snapshot",
    )

