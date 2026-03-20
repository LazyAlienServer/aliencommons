from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .mixins import UUIDPrimaryKeyMixin


class ScheduledTask(UUIDPrimaryKeyMixin, models.Model):
    """
    Fields:
     - id: primary key field, provided by 'UUIDPrimaryKeyMixin'
     - name: human-readable name for the scheduled task.
     - task_path: path of the task function e.g. 'articles.tasks.clear_unreferenced_images'
     - queue_name: name of the queue that this task belongs to
     - interval_seconds: time in seconds between two task executions
     - args_json: task arguments in JSON (to be db-friendly)
     - kwargs_json: task keyword arguments in JSON (to be db-friendly)
     - is_enabled: only enabled tasks will be queued
     - next_run_at: used to decide if the task will be executed
     - last_enqueued_at: a field for investigation and display
    """

    name = models.CharField(
        verbose_name=_("name"),
        max_length=100
    )
    task_path = models.CharField(
        verbose_name=_("task path"),
        max_length=255
    )
    queue_name = models.CharField(
        verbose_name=_("queue name"),
        max_length=100
    )
    interval_seconds = models.IntegerField(
        verbose_name=_("interval in seconds")
    )
    args_json = models.JSONField(
        verbose_name=_("arguments"),
        default=list, blank=True
    )
    kwargs_json = models.JSONField(
        verbose_name=_("keyword arguments"),
        default=dict, blank=True
    )
    is_enabled = models.BooleanField(
        verbose_name=_("enabled"),
        default=True, db_index=True
    )
    next_run_at = models.DateTimeField(
        verbose_name=_("next run at"),
        default=timezone.now, blank=True, db_index=True
    )
    last_enqueued_at = models.DateTimeField(
        verbose_name=_("last enqueued at"),
        null=True, blank=True
    )

    class Meta:
        verbose_name = _("scheduled task")
        verbose_name_plural = _("scheduled tasks")

        constraints = [
            models.CheckConstraint(
                condition=models.Q(interval_seconds__gt=0),
                name='interval_seconds_greater_than_0'
            ),
        ]

    def __str__(self):
        return self.name
