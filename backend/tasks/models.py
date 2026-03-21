from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.model_mixins import UUIDPrimaryKeyMixin


class IntervalSchedule(models.Model):
    """
    Schedule executing on a regular interval.
    """
    class Periods(models.TextChoices):
        SECONDS = 'seconds', _('seconds')
        MINUTES = 'minutes', _('minutes')
        DAYS = 'days', _('days')
        WEEKS = 'weeks', _('weeks')

    every = models.PositiveIntegerField(
        verbose_name=_("number of periods"),
        help_text=_("Number of interval periods to wait before next execution"),
    )
    period = models.CharField(
        verbose_name=_("interval period"),
        max_length=50, choices=Periods,
        help_text=_("The type of period used by the schedule")
    )

    class Meta:
        verbose_name = _("interval schedule")
        verbose_name_plural = _("interval schedules")

    def __str__(self):
        return f"every {self.every} {self.period}"


class PeriodicTask(UUIDPrimaryKeyMixin, models.Model):
    """
    Model representing a periodic task.
    """

    name = models.CharField(
        max_length=150,
        verbose_name=_("name"),
        help_text=_("A short description for this task"),
    )
    description = models.TextField(
        blank=True, default="",
        verbose_name=_("description"),
        help_text=_("A extended description for this task"),
    )
    task_path = models.CharField(
        max_length=255,
        verbose_name=_("task path"),
        help_text=_("The path of the task function to be run")
    )
    queue_name = models.CharField(
        max_length=100,
        verbose_name=_("queue name"),
        help_text=_("The name of the queue that this task belongs to"),
    )
    interval = models.ForeignKey(
        IntervalSchedule, on_delete=models.PROTECT,
        verbose_name=_("interval"),
        help_text=_("The time between two task executions"),
    )
    args = models.JSONField(
        default=list, blank=True,
        verbose_name=_("positional arguments"),
        help_text=_("The positional arguments passed to the function"),
    )
    kwargs = models.JSONField(
        default=dict, blank=True,
        verbose_name=_("keyword arguments"),
        help_text=_("The keyword arguments passed to the function"),
    )
    is_enabled = models.BooleanField(
        default=True, db_index=True,
        verbose_name=_("enabled"),
        help_text=_("Only enabled tasks will be queued"),
    )
    started_at = models.DateTimeField(
        default=timezone.now, blank=True, db_index=True,
        verbose_name=_("start at"),
        help_text=_("The start time of the task"),
    )
    next_run_at = models.DateTimeField(
        blank=True,
        verbose_name=_("next run at"),
        help_text=_("The next run time of the task"),
    )
    last_run_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("last run at"),
        help_text=_("The last run time of the task"),
    )

    class Meta:
        verbose_name = _("periodic task")
        verbose_name_plural = _("periodic tasks")

        ordering = ["-next_run_at",]

    def __str__(self):
        return self.name
