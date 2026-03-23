from django.core.management.base import BaseCommand

import time
import logging

from tasks.schedulers import run_due_schedules
from tasks.models import PeriodicTask

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run the periodic task scheduler"

    def handle(self, *args, **options):
        try:
            while True:
                try:
                    result = run_due_schedules(PeriodicTask.objects.filter(is_enabled=True))

                    logger.info(
                        "Scheduler tick completed",
                        extra={
                            "scanned": result.scanned,
                            "enqueued": result.enqueued,
                            "skipped": result.skipped,
                        }
                    )

                except Exception:
                    logger.exception("Exception while running periodic task")

                time.sleep(2)

        except KeyboardInterrupt:
            logger.exception("Keyborad Interruption while running periodic task")
