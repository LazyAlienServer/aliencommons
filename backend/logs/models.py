from django.db import models
from django.utils.translation import gettext_lazy as _


class FrontendLog(models.Model):
    LEVEL_CHOICES = [
        ('debug', 'DEBUG'),
        ('info', 'INFO'),
        ('warn', 'WARN'),
        ('error', 'ERROR'),
    ]

    level = models.CharField(
        verbose_name=_("level"),
        max_length=10, choices=LEVEL_CHOICES, db_index=True, editable=False
    )
    message = models.TextField(
        verbose_name=_("message"),
        editable=False
    )
    extra = models.JSONField(
        verbose_name=_("extra"),
        null=True, blank=True, editable=False
    )
    timestamp = models.DateTimeField(
        verbose_name=_("timestamp"),
        editable=False
    )
    page = models.CharField(
        verbose_name=_("page"),
        max_length=255, editable=False
    )
    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        auto_now_add=True, db_index=True, editable=False
    )

    class Meta:
        verbose_name = 'frontend log'
        verbose_name_plural = 'frontend logs'

    def __str__(self):
        return f"[{self.level.upper()}]: {self.page} - {self.message[:50]}"
