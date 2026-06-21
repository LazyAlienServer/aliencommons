from django.contrib import admin, messages

from .models import (
    Collection,
    CollectionItem,
    Article,
    ArticleSource,
    ArticlePublication,
    ArticlePublicationVersion,
    ArticleSnapshot,
    ArticleEvent,
)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    model = Article
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

    search_fields = ("source__title", "author__username")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"

    readonly_fields = ("id", "created_at", "updated_at", "last_moderation_at")

    fieldsets = [
        ("Basic", {"fields": ("id",)}),
        ("Ownership & Status", {"fields": ("author", "status", "is_deleted")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    ]

    actions = ["action_soft_delete", "action_restore", "action_hard_delete"]

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = "Status"

    def title(self, obj):
        return obj.source.title
    title.short_description = "Title"

    def action_soft_delete(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.is_deleted = True
            obj.save(update_fields=["is_deleted"])
            count += 1

        self.message_user(request, f"Soft-deleted {count} article(s).", level=messages.WARNING)
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


@admin.register(ArticleSource)
class ArticleSourceAdmin(admin.ModelAdmin):
    model = ArticleSource
    list_display = (
        "title",
        "article",
        "version",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "created_at",
    )
    search_fields = ("title", "article__author__username")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"
    readonly_fields = ("id", "article", "created_at", "updated_at")

    fieldsets = [
        ("Basic", {"fields": ("id", "article", "title", "markdown", "version")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    ]


@admin.register(ArticlePublication)
class ArticlePublicationAdmin(admin.ModelAdmin):
    model = ArticlePublication
    list_display = (
        "article",
        "latest_title",
        "latest_version_number",
        "published_at",
        "created_at",
    )
    list_filter = (
        "created_at",
    )

    search_fields = ("versions__title", "article__source__title", "article__author__username")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"

    readonly_fields = ("id", "created_at", "updated_at", "article", "published_at")

    fieldsets = [
        ("Basic", {"fields": ("id", "article")}),
        ("Timestamps", {"fields": ("published_at", "created_at", "updated_at")}),
    ]

    def latest_title(self, obj):
        latest_version = obj.latest_version()
        return latest_version.title if latest_version else None
    latest_title.short_description = "Latest title"

    def latest_version_number(self, obj):
        latest_version = obj.latest_version()
        return latest_version.version if latest_version else None
    latest_version_number.short_description = "Latest version"


@admin.register(ArticlePublicationVersion)
class ArticlePublicationVersionAdmin(admin.ModelAdmin):
    model = ArticlePublicationVersion
    list_display = (
        "publication",
        "version",
        "title",
        "publication_at",
        "created_at",
    )
    list_filter = (
        "publication_at",
        "created_at",
    )

    search_fields = ("title", "publication__article__source__title", "publication__article__author__username")
    ordering = ("-publication_at",)
    list_per_page = 25
    date_hierarchy = "publication_at"

    readonly_fields = (
        "id",
        "publication",
        "approved_snapshot",
        "version",
        "title",
        "html",
        "publication_at",
        "created_at",
        "updated_at",
    )

    fieldsets = [
        ("Basic", {"fields": ("id", "publication", "version", "title", "html")}),
        ("Key Info", {"fields": ("approved_snapshot",)}),
        ("Timestamps", {"fields": ("publication_at", "created_at", "updated_at")}),
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
        "id", "created_at", "article", "title", "markdown", "hash",
        "moderation_status", "moderation_status_display",
    )

    fieldsets = [
        ("Basic", {"fields": ("id", "title", "markdown", "hash")}),
        ("Key Info", {"fields": ("article", "moderation_status", "moderation_status_display")}),
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

    readonly_fields = ("id", "article", "article_snapshot", "event_type", "actor", "created_at")

    fieldsets = [
        ("Key Info", {
            "fields": ("id", "event_type", "actor", "article", "article_snapshot")
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    ]

    def type_display(self, obj):
        return obj.get_event_type_display()
    type_display.short_description = "Type"


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    model = Collection
    list_display = (
        "title",
        "author",
        "created_at",
        "updated_at",
    )
    list_filter = (
        ("author", admin.RelatedOnlyFieldListFilter),
        "created_at",
    )
    search_fields = ("title", "description", "author__username")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = [
        ("Basic", {"fields": ("id", "title", "description")}),
        ("Ownership", {"fields": ("author",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    ]


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    model = CollectionItem
    list_display = (
        "collection",
        "article_publication",
        "position",
        "created_at",
    )
    list_filter = (
        "collection",
        "created_at",
    )
    search_fields = ("collection__title", "article_publication__versions__title")
    ordering = ("collection", "position")
    list_per_page = 25
    date_hierarchy = "created_at"
    readonly_fields = ("id", "created_at")

    fieldsets = [
        ("Basic", {"fields": ("id", "collection", "article_publication", "position")}),
        ("Timestamps", {"fields": ("created_at",)}),
    ]
