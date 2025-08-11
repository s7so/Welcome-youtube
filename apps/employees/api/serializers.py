from rest_framework import serializers
from apps.employees.models import Employee, Department


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "full_name",
            "job_title",
            "department",
            "department_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]