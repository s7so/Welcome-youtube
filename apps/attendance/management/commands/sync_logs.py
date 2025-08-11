import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync attendance logs from FingerTec device (skeleton)."

    def handle(self, *args, **options):
        logger.info("Sync attendance command invoked (skeleton).")
        try:
            # Deferred import to avoid hard dependency before implementation
            try:
                from attendance.tasks.sync import run_sync_job  # type: ignore
            except Exception:  # pragma: no cover
                run_sync_job = None

            if run_sync_job is None:
                logger.warning("run_sync_job not implemented yet. Skipping execution.")
                self.stdout.write(self.style.WARNING("[SKIP] run_sync_job not implemented yet."))
                return

            run_sync_job()
            self.stdout.write(self.style.SUCCESS("[OK] Sync job executed."))
        except Exception as exc:  # pragma: no cover
            logger.exception("Unexpected error while running sync command", exc_info=exc)
            self.stderr.write(self.style.ERROR(f"[ERR] {exc}"))