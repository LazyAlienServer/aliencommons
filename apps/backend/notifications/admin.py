from django.contrib import admin

from .models import NotificationDelivery, NotificationEvent


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = ("id", "reason", "channel", "actor", "target", "delivery_status", "created_at")
    list_filter = ("reason", "channel", "delivery_status", "created_at")
    search_fields = ("dedupe_key", "actor__username")
    readonly_fields = ("id", "created_at", "updated_at", "delivered_at")


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "event", "read_at", "created_at")
    list_filter = ("read_at", "created_at")
    search_fields = ("recipient__username", "event__dedupe_key")
    readonly_fields = ("id", "created_at", "updated_at")
