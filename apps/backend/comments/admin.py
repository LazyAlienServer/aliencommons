from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = (
        "id",
        "author",
        "target",
        "parent",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_deleted",
        "created_at",
        ("author", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("body", "author__username")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")

