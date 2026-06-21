from django.contrib import admin

from .models import Bookmark, BookmarkFolder


@admin.register(BookmarkFolder)
class BookmarkFolderAdmin(admin.ModelAdmin):
    model = BookmarkFolder
    list_display = ("name", "user", "created_at", "updated_at")
    list_filter = (("user", admin.RelatedOnlyFieldListFilter), "created_at")
    search_fields = ("name", "user__username")
    ordering = ("user", "created_at")
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = [
        ("Basic", {"fields": ("id", "user", "name")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    ]


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    model = Bookmark
    list_display = ("user", "folder", "article_publication", "created_at")
    list_filter = (("user", admin.RelatedOnlyFieldListFilter), "folder", "created_at")
    search_fields = (
        "user__username",
        "folder__name",
        "article_publication__title",
    )
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")

    fieldsets = [
        ("Basic", {"fields": ("id", "user", "folder", "article_publication")}),
        ("Timestamps", {"fields": ("created_at",)}),
    ]
