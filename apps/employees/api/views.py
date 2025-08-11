from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
import csv
from io import TextIOWrapper

from apps.employees.models import Employee, Department
from .serializers import EmployeeSerializer
from apps.core.permissions import IsAuditorOrReadOnly, IsDeptManagerReadOnly, IsHRAdmin


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("department").all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAuditorOrReadOnly, IsDeptManagerReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["employee_id", "full_name", "job_title", "department__name"]
    ordering_fields = ["employee_id", "full_name", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        dept = self.request.query_params.get("department")
        is_active = self.request.query_params.get("is_active")
        if dept:
            qs = qs.filter(department_id=dept)
        if is_active is not None:
            if is_active.lower() in ("1", "true", "yes"):
                qs = qs.filter(is_active=True)
            elif is_active.lower() in ("0", "false", "no"):
                qs = qs.filter(is_active=False)
        return qs

    @action(detail=False, methods=["post"], url_path="bulk-upload", permission_classes=[IsAuthenticated, IsHRAdmin], parser_classes=[MultiPartParser, FormParser])
    def bulk_upload(self, request):
        """
        Upload CSV with headers: employee_id,full_name,department,job_title,is_active
        - Upsert by employee_id
        - department: matched by name (created if not exists)
        - is_active: true/false/1/0 (optional; default true)
        Optional query/form param: dry_run=true to validate without saving
        """
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "file is required"}, status=status.HTTP_400_BAD_REQUEST)

        dry_run = str(request.data.get("dry_run", "false")).lower() in {"1", "true", "yes"}

        try:
            wrapper = TextIOWrapper(file_obj.file, encoding="utf-8")
            reader = csv.DictReader(wrapper)
        except Exception:
            return Response({"detail": "invalid CSV file"}, status=status.HTTP_400_BAD_REQUEST)

        required_cols = {"employee_id", "full_name"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            return Response({"detail": f"CSV must contain columns: {', '.join(sorted(required_cols))}"}, status=status.HTTP_400_BAD_REQUEST)

        created = 0
        updated = 0
        errors = []
        row_num = 1  # header is row 1

        @transaction.atomic
        def process_rows():
            nonlocal created, updated, errors, row_num
            for row in reader:
                row_num += 1
                emp_id = (row.get("employee_id") or "").strip()
                full_name = (row.get("full_name") or "").strip()
                job_title = (row.get("job_title") or "").strip() or None
                dept_name = (row.get("department") or "").strip() or None
                is_active_val = row.get("is_active")
                if not emp_id or not full_name:
                    errors.append({"row": row_num, "error": "employee_id and full_name are required"})
                    continue
                if len(emp_id) > 20 or len(full_name) > 100:
                    errors.append({"row": row_num, "error": "field length exceeded"})
                    continue
                is_active = True
                if is_active_val is not None and str(is_active_val).strip() != "":
                    sval = str(is_active_val).lower()
                    if sval in ("1", "true", "yes"): is_active = True
                    elif sval in ("0", "false", "no"): is_active = False
                dept = None
                if dept_name:
                    dept, _ = Department.objects.get_or_create(name=dept_name)
                obj, exists = Employee.objects.get_or_create(employee_id=emp_id, defaults={
                    "full_name": full_name,
                    "job_title": job_title,
                    "department": dept,
                    "is_active": is_active,
                })
                if exists:
                    updated_fields = {}
                    if obj.full_name != full_name: updated_fields["full_name"] = full_name
                    if obj.job_title != job_title: updated_fields["job_title"] = job_title
                    if obj.department_id != (dept.id if dept else None): updated_fields["department"] = dept
                    if obj.is_active != is_active: updated_fields["is_active"] = is_active
                    if updated_fields:
                        for k, v in updated_fields.items(): setattr(obj, k, v)
                        obj.save(update_fields=list(updated_fields.keys()))
                        updated += 1
                else:
                    created += 1

            if dry_run:
                raise transaction.TransactionManagementError("DRY_RUN")

        try:
            process_rows()
        except transaction.TransactionManagementError as e:
            if str(e) != "DRY_RUN":
                return Response({"detail": "transaction error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "created": created,
            "updated": updated,
            "errors": errors,
            "dry_run": dry_run,
        })