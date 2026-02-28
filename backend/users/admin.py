from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


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
            'fields': ('email', 'password1', 'password2'),
        }),
    )
