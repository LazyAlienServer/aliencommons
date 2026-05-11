from django.contrib import admin

from .models import CommunityPost


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "created_at",
        "updated_at",
        "is_deleted",
    )
    list_filter = ("is_deleted", "created_at")
    search_fields = ("body", "author__username")
    ordering = ("-created_at",)
