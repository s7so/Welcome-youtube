from __future__ import annotations
import logging
from contextlib import contextmanager
from datetime import datetime, timezone

from django.conf import settings
from django.db import connection, transaction

from apps.attendance.models import AttendanceLog, SyncState
from apps.employees.models import Employee
from apps.integrations.fingertec.client import FingerTecClient, ConnectionError
from apps.platform.alerting.alerter import send_critical

logger = logging.getLogger(__name__)


@contextmanager
def pg_advisory_lock(lock_key: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(%s);", [lock_key])
        acquired = cursor.fetchone()[0]
    try:
        if not acquired:
            yield False
            return
        yield True
    finally:
        if acquired:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_unlock(%s);", [lock_key])


def get_last_sync_time() -> datetime | None:
    state, _ = SyncState.objects.get_or_create(key="attendance")
    return state.last_sync_time


def set_last_sync_time(ts: datetime) -> None:
    SyncState.objects.update_or_create(
        key="attendance", defaults={"last_sync_time": ts}
    )


def run_sync_job() -> None:
    logger.info("run_sync_job started")

    LOCK_KEY = 814_215  # arbitrary app-level lock id
    with pg_advisory_lock(LOCK_KEY) as acquired:
        if not acquired:
            logger.info("Sync job is already running. Skipping this run.")
            return

        last_sync = get_last_sync_time()
        if last_sync is None:
            last_sync = datetime(2000, 1, 1, tzinfo=timezone.utc)
        logger.info("Starting sync for logs after: %s", last_sync.isoformat())

        try:
            client = FingerTecClient(
                ip=getattr(settings, "FINGERTEC_IP", None),
                port=int(getattr(settings, "FINGERTEC_PORT", 0) or 0),
            )
            client.connect()
            raw_logs = client.get_new_logs(since=last_sync)
        except ConnectionError as exc:
            logger.error("Failed to connect to FingerTec device.", exc_info=exc)
            send_critical("FingerTec device is offline!")
            return

        raw_logs = list(raw_logs or [])
        if not raw_logs:
            logger.info("No new attendance logs found.")
            return

        new_logs_count = 0
        latest_log_time: datetime | None = None

        with transaction.atomic():
            for raw in raw_logs:
                log = client.parse(raw)
                emp = Employee.objects.filter(employee_id=log.employee_id).first()
                if not emp:
                    logger.warning(
                        "Skipping log for unknown employee ID: %s", log.employee_id
                    )
                    continue

                exists = AttendanceLog.objects.filter(
                    employee=emp, check_time=log.timestamp
                ).exists()
                if exists:
                    logger.info(
                        "Skipping duplicate log for employee %s at %s",
                        emp.employee_id,
                        log.timestamp,
                    )
                    continue

                AttendanceLog.objects.create(
                    employee=emp,
                    check_time=log.timestamp,
                    log_type=log.type,
                    source="FingerTec Device",
                )
                new_logs_count += 1
                latest_log_time = (
                    max(latest_log_time, log.timestamp)
                    if latest_log_time is not None
                    else log.timestamp
                )

            if new_logs_count > 0 and latest_log_time is not None:
                set_last_sync_time(latest_log_time)

        logger.info("Successfully synced %d new attendance logs.", new_logs_count)