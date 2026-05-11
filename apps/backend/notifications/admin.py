from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    model = Notification
    list_display = (
        "recipient",
        "notification_type",
        "verb",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = (
        "recipient__username",
        "verb",
        "dedupe_key",
    )
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
