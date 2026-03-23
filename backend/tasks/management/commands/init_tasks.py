from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from datetime import timedelta

from tasks.models import IntervalSchedule, PeriodicTask
from tasks.periodic_tasks_registry import periodic_tasks


class Command(BaseCommand):
    help = "Initialize all tasks"

    def handle(self, *args, **options):
        task_configs = periodic_tasks

        # Init tasks
        for config in task_configs:

            required_schedule = config["schedule"]

            try:
                period = IntervalSchedule.Periods(required_schedule["period"])
            except ValueError as exc:
                raise ImproperlyConfigured(
                    f"Invalid period configured {required_schedule['period']}"
                ) from exc

            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=required_schedule['every'],
                period=period,
            )

            # Create all uncreated tasks in task_configs
            task, _ = PeriodicTask.objects.update_or_create(
                name=config["name"],
                defaults={
                    "description": config.get("description", ""),
                    "task": config["task"],
                    "queue_name": config.get("queue_name", "default"),
                    "interval": schedule,
                    "args": config.get("args", []),
                    "kwargs": config.get("kwargs", {}),
                    "is_enabled": config.get("is_enabled", True),
                    "next_run_at": timezone.now() + timedelta(seconds=schedule.in_seconds),
                },
            )

        # Delete all orphan tasks
        existing_tasks = PeriodicTask.objects.all()
        required_names = [config["name"] for config in task_configs]

        for task in existing_tasks:
            if task.name not in required_names:
                self.stdout.write(
                    self.style.WARNING(f"Deleting old task: {task.name} ({task.task})")
                )
                task.delete()

        # Delete all orphan schedules
        orphan_schedules = IntervalSchedule.objects.filter(periodic_tasks__isnull=True)
        for schedule in orphan_schedules:
            schedule.delete()

        self.stdout.write(self.style.SUCCESS('Successfully initialized tasks.'))
