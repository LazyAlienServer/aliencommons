from django.contrib import admin

from .models import Reaction


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
    search_fields = (
        "user__username",
        "target__article_publication__title",
        "target__comment__body",
    )
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at")
