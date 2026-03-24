from django.contrib import admin, messages

from .models import SourceArticle, PublishedArticle, ArticleSnapshot, ArticleEvent


@admin.register(SourceArticle)
class SourceArticleAdmin(admin.ModelAdmin):
    model = SourceArticle
    list_display = (
        "title",
        "author",
        "status_display",
        "created_at",
        "updated_at",
        "is_deleted",
    )
    list_filter = (
        "status",
        "is_deleted",
        ("author", admin.RelatedOnlyFieldListFilter),
        "created_at",
    )

    search_fields = ("title", "author__username")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"

    readonly_fields = ("id", "created_at", "updated_at", "last_moderation_at")

    fieldsets = [
        ("Basic", {"fields": ("id", "title", "content")}),
        ("Ownership & Status", {"fields": ("author", "status", "is_deleted")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    ]

    actions = ["action_soft_delete", "action_restore", "action_hard_delete"]

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = "Status"

    def action_soft_delete(self, request, queryset):
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f"Soft-deleted {updated} article(s).", level=messages.WARNING)
    action_soft_delete.short_description = "Soft delete selected"

    def action_restore(self, request, queryset):
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f"Restored {updated} article(s).", level=messages.SUCCESS)
    action_restore.short_description = "Restore selected (undo soft delete)"

    def action_hard_delete(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.hard_delete()
            count += 1
        self.message_user(request, f"Hard-deleted {count} article(s).", level=messages.ERROR)
    action_hard_delete.short_description = "Hard delete selected (cannot be undone)"


@admin.register(PublishedArticle)
class PublishedArticleAdmin(admin.ModelAdmin):
    model = PublishedArticle
    list_display = (
        "title",
        "created_at",
    )
    list_filter = (
        "created_at",
    )

    search_fields = ("title",)
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"

    readonly_fields = ("id", "created_at", "source_article", "title", "content")

    fieldsets = [
        ("Basic", {"fields": ("id", "title", "content")}),
        ("Key Info", {"fields": ("source_article", )}),
        ("Timestamps", {"fields": ("created_at",)}),
    ]


@admin.register(ArticleSnapshot)
class ArticleSnapshotAdmin(admin.ModelAdmin):
    model = ArticleSnapshot
    list_display = (
        "title",
        "created_at",
        "moderation_status_display",
    )
    list_filter = (
        "created_at",
        "moderation_status",
    )

    search_fields = ("title", "creator__username")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"

    readonly_fields = (
        "id", "created_at", "source_article", "title", "content", "content_hash",
        "moderation_status", "moderation_status_display",
    )

    fieldsets = [
        ("Basic", {"fields": ("id", "title", "content", "content_hash")}),
        ("Key Info", {"fields": ("source_article", "moderation_status", "moderation_status_display")}),
        ("Timestamps", {"fields": ("created_at",)}),
    ]

    def moderation_status_display(self, obj):
        return obj.get_moderation_status_display()


@admin.register(ArticleEvent)
class ArticleEventAdmin(admin.ModelAdmin):
    model = ArticleEvent
    list_display = (
        "actor",
        "event_type",
        "created_at",
    )

    list_filter = (
        "actor",
        "event_type",
        "created_at",
    )

    search_fields = ("event_type", "actor__username")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"

    readonly_fields = ("id", "source_article", "article_snapshot", "event_type", "actor", "created_at")

    fieldsets = [
        ("Key Info", {
            "fields": ("id", "event_type", "actor", "source_article", "article_snapshot", "annotation")
        }),
        ("Timestamps", {"fields": ("created_at",)}),
    ]

    def type_display(self, obj):
        return obj.get_event_type_display()
    type_display.short_description = "Type"
