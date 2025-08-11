from django.contrib import admin
from django.contrib import messages
from django.http import HttpRequest
from .models import AttendanceLog, SyncState
from .tasks.sync import run_sync_job


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ("employee", "check_time", "log_type", "source", "created_at")
    list_filter = ("log_type", "source")
    search_fields = ("employee__employee_id", "employee__full_name")


@admin.register(SyncState)
class SyncStateAdmin(admin.ModelAdmin):
    list_display = ("key", "last_sync_time", "updated_at")
    search_fields = ("key",)
    actions = ["run_sync_now"]

    def run_sync_now(self, request: HttpRequest, queryset):
        run_sync_job()
        self.message_user(request, "تم تشغيل مهمة المزامنة بنجاح (راجع السجلات).", level=messages.INFO)

    run_sync_now.short_description = "تشغيل المزامنة الآن"