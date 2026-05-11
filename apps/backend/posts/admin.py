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
    search_fields = ("body",)
    ordering = ("-created_at",)
