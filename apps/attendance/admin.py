from django.contrib import admin
from .models import AttendanceLog, SyncState


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ("employee", "check_time", "log_type", "source", "created_at")
    list_filter = ("log_type", "source")
    search_fields = ("employee__employee_id", "employee__full_name")


@admin.register(SyncState)
class SyncStateAdmin(admin.ModelAdmin):
    list_display = ("key", "last_sync_time", "updated_at")
    search_fields = ("key",)