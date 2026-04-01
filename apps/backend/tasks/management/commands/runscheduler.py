from django.core.management.base import BaseCommand

import time

from tasks.schedulers import enqueue_due_tasks
from tasks.models import PeriodicTask
from logs.logging.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Run the periodic task scheduler"

    def handle(self, *args, **options):
        try:
            while True:
                try:
                    result = enqueue_due_tasks(
                        PeriodicTask.objects.filter(is_enabled=True)
                    )

                    logger.info(
                        "Scheduler tick completed",
                        extra={
                            "scanned": result.scanned,
                            "enqueued": result.enqueued,
                            "failed": result.failed,
                        }
                    )

                except Exception:
                    logger.exception("Exception while running periodic task")

                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("Keyboard Interruption")
