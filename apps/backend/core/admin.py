from django.contrib import admin

from .models import ContentTarget


@admin.register(ContentTarget)
class ContentTargetAdmin(admin.ModelAdmin):
    model = ContentTarget
    list_display = (
        "target_type",
        "published_article",
        "comment",
        "created_at",
    )
    list_filter = ("target_type", "created_at")
    search_fields = ("published_article__title", "comment__body")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")
