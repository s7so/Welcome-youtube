from datetime import datetime
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_datetime
from django.db.models import Q

from apps.attendance.models import AttendanceLog
from .serializers import AttendanceLogSerializer
from apps.core.permissions import IsDeptManagerReadOnly, IsAuditorOrReadOnly


class AttendanceLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttendanceLog.objects.select_related("employee").all()
    serializer_class = AttendanceLogSerializer
    permission_classes = [IsAuthenticated, IsDeptManagerReadOnly, IsAuditorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "employee__employee_id",
        "employee__full_name",
        "source",
    ]
    ordering_fields = ["check_time", "created_at"]
    ordering = ["-check_time"]

    def get_queryset(self):
        qs = super().get_queryset()
        employee_id = self.request.query_params.get("employee_id")
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        log_type = self.request.query_params.get("log_type")

        if employee_id:
            qs = qs.filter(employee__employee_id=employee_id)
        if log_type in ("IN", "OUT"):
            qs = qs.filter(log_type=log_type)
        if start:
            dt = parse_datetime(start)
            if dt:
                qs = qs.filter(check_time__gte=dt)
        if end:
            dt = parse_datetime(end)
            if dt:
                qs = qs.filter(check_time__lte=dt)
        return qs