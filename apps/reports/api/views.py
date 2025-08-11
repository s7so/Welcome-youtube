from datetime import datetime
from typing import Any, Dict, List
import csv
from io import StringIO

from django.db.models import Min, Max, Count, Q
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse

from apps.attendance.models import AttendanceLog
from apps.employees.models import Employee
from apps.core.permissions import IsDeptManagerReadOnly, IsAuditorOrReadOnly
from .serializers import (
    MonthlyReportResponseSerializer,
    WorkHoursReportResponseSerializer,
)


class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated, IsDeptManagerReadOnly, IsAuditorOrReadOnly]

    def get(self, request, *args, **kwargs):
        department_id = request.query_params.get("department")
        start_param = request.query_params.get("start")
        end_param = request.query_params.get("end")
        export = request.query_params.get("export")  # 'csv' optional

        if not start_param or not end_param:
            return Response({"detail": "start and end are required ISO datetimes"}, status=400)

        start = parse_datetime(start_param)
        end = parse_datetime(end_param)
        if not start or not end or start > end:
            return Response({"detail": "invalid start/end"}, status=400)

        logs = AttendanceLog.objects.select_related("employee", "employee__department").filter(
            check_time__gte=start, check_time__lte=end
        )
        if department_id:
            logs = logs.filter(employee__department_id=department_id)

        # Aggregate per employee
        agg = logs.values(
            "employee_id",
            "employee__employee_id",
            "employee__full_name",
            "employee__department__name",
        ).annotate(
            total_logs=Count("id"),
            first_seen=Min("check_time"),
            last_seen=Max("check_time"),
            first_check_in=Min("check_time", filter=Q(log_type="IN")),
            last_check_out=Max("check_time", filter=Q(log_type="OUT")),
        ).order_by("employee__full_name")

        results: List[Dict[str, Any]] = []
        for row in agg:
            results.append({
                "employee_id": row["employee_id"],
                "employee_identifier": row["employee__employee_id"],
                "full_name": row["employee__full_name"],
                "department_name": row["employee__department__name"],
                "total_logs": row["total_logs"],
                "first_check_in": row["first_check_in"],
                "last_check_out": row["last_check_out"],
                "first_seen": row["first_seen"],
                "last_seen": row["last_seen"],
            })

        if export == "csv":
            return self._export_csv(results, start, end, department_id)

        payload = {
            "department": department_id,
            "start": start,
            "end": end,
            "count": len(results),
            "results": results,
        }
        serializer = MonthlyReportResponseSerializer(payload)
        return Response(serializer.data)

    def _export_csv(self, results: List[Dict[str, Any]], start, end, department_id):
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "employee_identifier",
            "full_name",
            "department_name",
            "total_logs",
            "first_check_in",
            "last_check_out",
            "first_seen",
            "last_seen",
        ])
        for r in results:
            writer.writerow([
                r["employee_identifier"],
                r["full_name"],
                r.get("department_name") or "",
                r["total_logs"],
                r.get("first_check_in") or "",
                r.get("last_check_out") or "",
                r.get("first_seen") or "",
                r.get("last_seen") or "",
            ])
        resp = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = (
            f"attachment; filename=monthly-report_{department_id or 'all'}_{start.date()}_{end.date()}.csv"
        )
        return resp


class DepartmentMonthlySummaryView(APIView):
    permission_classes = [IsAuthenticated, IsDeptManagerReadOnly, IsAuditorOrReadOnly]

    def get(self, request, *args, **kwargs):
        start_param = request.query_params.get("start")
        end_param = request.query_params.get("end")
        if not start_param or not end_param:
            return Response({"detail": "start and end are required ISO datetimes"}, status=400)
        start = parse_datetime(start_param)
        end = parse_datetime(end_param)
        if not start or not end or start > end:
            return Response({"detail": "invalid start/end"}, status=400)

        logs = AttendanceLog.objects.select_related("employee", "employee__department").filter(
            check_time__gte=start, check_time__lte=end
        )
        agg = logs.values("employee__department__id", "employee__department__name").annotate(
            employees_count=Count("employee", distinct=True),
            logs_count=Count("id"),
            first_seen=Min("check_time"),
            last_seen=Max("check_time"),
        ).order_by("employee__department__name")

        data = [
            {
                "department_id": row["employee__department__id"],
                "department_name": row["employee__department__name"],
                "employees_count": row["employees_count"],
                "logs_count": row["logs_count"],
                "first_seen": row["first_seen"],
                "last_seen": row["last_seen"],
            }
            for row in agg
        ]
        return Response({
            "start": start,
            "end": end,
            "count": len(data),
            "results": data,
        })


class WorkHoursMonthlyReportView(APIView):
    permission_classes = [IsAuthenticated, IsDeptManagerReadOnly, IsAuditorOrReadOnly]

    def get(self, request, *args, **kwargs):
        department_id = request.query_params.get("department")
        start_param = request.query_params.get("start")
        end_param = request.query_params.get("end")
        if not start_param or not end_param:
            return Response({"detail": "start and end are required ISO datetimes"}, status=400)
        start = parse_datetime(start_param)
        end = parse_datetime(end_param)
        if not start or not end or start > end:
            return Response({"detail": "invalid start/end"}, status=400)

        logs_qs = AttendanceLog.objects.select_related("employee", "employee__department").filter(
            check_time__gte=start, check_time__lte=end
        )
        if department_id:
            logs_qs = logs_qs.filter(employee__department_id=department_id)

        # Pull all logs ordered by employee and time
        logs_qs = logs_qs.order_by("employee_id", "check_time")

        results: List[Dict[str, Any]] = []
        # Iterate per employee
        current_emp = None
        buffer: List[AttendanceLog] = []
        for log in logs_qs.iterator():
            if current_emp is None:
                current_emp = log.employee_id
            if log.employee_id != current_emp:
                # process buffer
                results.append(self._summarize(buffer))
                buffer = []
                current_emp = log.employee_id
            buffer.append(log)
        if buffer:
            results.append(self._summarize(buffer))

        # Fill identity fields from first log of each buffer
        for r in results:
            emp = Employee.objects.select_related("department").get(id=r["employee_id"])  # guaranteed by logs
            r.update(
                employee_identifier=emp.employee_id,
                full_name=emp.full_name,
                department_name=(emp.department.name if emp.department else None),
                total_hours=round(r["total_seconds"] / 3600.0, 2),
            )

        payload = {
            "department": department_id,
            "start": start,
            "end": end,
            "count": len(results),
            "results": results,
        }
        serializer = WorkHoursReportResponseSerializer(payload)
        return Response(serializer.data)

    def _summarize(self, logs: List[AttendanceLog]) -> Dict[str, Any]:
        seconds = 0
        sessions = 0
        i = 0
        while i < len(logs):
            if logs[i].log_type == "IN":
                # find next OUT
                j = i + 1
                while j < len(logs) and logs[j].log_type != "OUT":
                    j += 1
                if j < len(logs) and logs[j].log_type == "OUT":
                    delta = (logs[j].check_time - logs[i].check_time).total_seconds()
                    if delta > 0:
                        seconds += int(delta)
                        sessions += 1
                    i = j + 1
                    continue
            i += 1
        return {
            "employee_id": logs[0].employee_id if logs else None,
            "sessions": sessions,
            "total_seconds": seconds,
        }