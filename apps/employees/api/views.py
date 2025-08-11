from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from apps.employees.models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("department").all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
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