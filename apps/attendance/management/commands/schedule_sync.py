from django.core.management.base import BaseCommand
from django.conf import settings
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json


class Command(BaseCommand):
    help = "Create or update Celery Beat schedule for attendance sync job."

    def handle(self, *args, **options):
        minutes = int(getattr(settings, "SYNC_INTERVAL_MINUTES", 5) or 5)
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=minutes, period=IntervalSchedule.MINUTES
        )
        task, created = PeriodicTask.objects.update_or_create(
            name="attendance_sync_job",
            defaults={
                "interval": schedule,
                "task": "attendance.run_sync_job",
                "args": json.dumps([]),
                "kwargs": json.dumps({}),
                "enabled": True,
            },
        )
        self.stdout.write(self.style.SUCCESS(
            f"[OK] Scheduled attendance sync every {minutes} minute(s)."
        ))