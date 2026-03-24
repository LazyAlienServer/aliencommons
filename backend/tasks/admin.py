from django.contrib import admin

from .models import IntervalSchedule, PeriodicTask


@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(admin.ModelAdmin):
    model = IntervalSchedule
    list_display = ("every", "period")
    list_filter = ("every", "period")
    search_fields = ("every", "period")

    ordering = ("every",)
    list_per_page = 25

    fieldsets = [
        ("Basic", {"fields": ("every", "period")}),
    ]


@admin.register(PeriodicTask)
class PeriodicTaskAdmin(admin.ModelAdmin):
    model = PeriodicTask
    list_display = (
        "name",
        "queue_name",
        "is_enabled",
        "next_enqueue_at",
    )

    list_filter = ("queue_name", "is_enabled")
    search_fields = ("name", "queue_name")

    readonly_fields = (
        "last_enqueued_at",
        "last_started_at",
        "last_finished_at",
    )

    fieldsets = [
        ("Basic", {"fields": ("name", "description", "queue_name", "interval", "is_enabled")}),
        ("Arguments", {"fields": ("args", "kwargs")}),
        ("Timestamps", {"fields": (
            "last_enqueued_at", "next_enqueue_at", "last_started_at", "last_finished_at"
        )}),
    ]
