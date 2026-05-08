from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from bookmarks.models import BookmarkFolder


User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'email', 'username', 'is_moderator')
    ordering = ('id',)
    search_fields = ('email', 'username')

    readonly_fields = ('id', 'date_joined', 'last_login')

    fieldsets = (
        (None, {
            'fields': ('id', 'email', 'password')
        }),
        ('Personal info', {
            'fields': ('username', 'avatar', 'signature')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_moderator', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
            return

        super().save_model(request, obj, form, change)
        BookmarkFolder.objects.create(user=obj, name=settings.DEFAULT_BOOKMARK_FOLDER_NAME)
