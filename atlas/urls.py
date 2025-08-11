from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.employees.api.views import EmployeeViewSet
from apps.attendance.api.views import AttendanceLogViewSet
from apps.reports.api.views import MonthlyReportView, DepartmentMonthlySummaryView, WorkHoursMonthlyReportView


def healthz(_request):
    return JsonResponse({"status": "ok"})


router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"attendance-logs", AttendanceLogViewSet, basename="attendance-log")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("_healthz", healthz),
    path("api/", include(router.urls)),
    path("api/reports/monthly", MonthlyReportView.as_view()),
    path("api/reports/monthly-by-department", DepartmentMonthlySummaryView.as_view()),
    path("api/reports/work-hours", WorkHoursMonthlyReportView.as_view()),
]