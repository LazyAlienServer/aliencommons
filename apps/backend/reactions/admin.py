from django.contrib import admin

from .models import Reaction, ReactionTarget


@admin.register(ReactionTarget)
class ReactionTargetAdmin(admin.ModelAdmin):
    model = ReactionTarget
    list_display = (
        "target_type",
        "published_article",
        "created_at",
    )
    list_filter = ("target_type", "created_at")
    search_fields = ("published_article__title",)
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    model = Reaction
    list_display = (
        "user",
        "target",
        "reaction_type",
        "created_at",
    )
    list_filter = ("reaction_type", "created_at")
    search_fields = ("user__username", "target__published_article__title")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")

