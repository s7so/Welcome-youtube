from django.db import models
from apps.employees.models import Employee


class AttendanceLog(models.Model):
    class LogType(models.TextChoices):
        IN = "IN", "IN"
        OUT = "OUT", "OUT"

    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendance_logs"
    )
    check_time = models.DateTimeField()
    log_type = models.CharField(max_length=3, choices=LogType.choices)
    source = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_logs"
        indexes = [
            models.Index(fields=["employee", "check_time"], name="idx_att_employee_time"),
            models.Index(fields=["check_time"], name="idx_att_time"),
        ]
        ordering = ["-check_time"]

    def __str__(self) -> str:
        return f"{self.employee.employee_id} {self.log_type} @ {self.check_time}"


class SyncState(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sync_state"
        verbose_name = "Sync State"
        verbose_name_plural = "Sync States"

    def __str__(self) -> str:
        return f"{self.key}: {self.last_sync_time}"