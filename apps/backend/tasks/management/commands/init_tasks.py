from django.core.management.base import BaseCommand, CommandError

from tasks.models import IntervalSchedule, PeriodicTask
from tasks.periodic_tasks_registry import periodic_tasks
from tasks.utils import compute_next_enqueue_at
from logs.logging import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Initialize all tasks"

    def handle(self, *args, **options):
        task_configs = periodic_tasks

        for config in task_configs:

            # Initialize schedules
            required_schedule = config["schedule"]
            try:
                period = IntervalSchedule.Periods(required_schedule["period"])
            except ValueError as exc:
                logger.exception(
                    f"Invalid period configured: {required_schedule['period']}"
                )

                raise CommandError(
                    f"Invalid period configured: {required_schedule['period']}"
                ) from exc

            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=required_schedule['every'],
                period=period,
            )
            logger.info(f"Schedule initialized: {schedule.__str__}")

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
                    "next_enqueue_at": compute_next_enqueue_at(schedule.in_seconds)
                },
            )
            logger.info(f"Schedule initialized: {schedule.__str__}")

        # Delete all orphan tasks
        existing_tasks = PeriodicTask.objects.all()
        required_names = [config["name"] for config in task_configs]

        for task in existing_tasks:
            if task.name not in required_names:
                logger.warning(f"Deleting old task: {task.name} ({task.task})")
                task.delete()

        # Delete all orphan schedules
        orphan_schedules = IntervalSchedule.objects.filter(periodic_tasks__isnull=True)
        for schedule in orphan_schedules:
            schedule.delete()

        logger.info("All tasks successfully initialized")
