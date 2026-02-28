from django.contrib import admin

from .models import FrontendLog


@admin.register(FrontendLog)
class FrontendLogAdmin(admin.ModelAdmin):
    model = FrontendLog
    list_display = ('level', 'message_short', 'page', 'timestamp', 'created_at')
    ordering = ('level', 'page', 'timestamp', 'created_at')
    search_fields = ('level', 'page', 'message')

    def message_short(self, obj):
        if len(obj.message) > 50:
            msg = obj.message[:50] + '...'
        else:
            msg = obj.message

        return msg

    message_short.short_description = 'Message'
