from rest_framework import serializers
from apps.attendance.models import AttendanceLog


class AttendanceLogSerializer(serializers.ModelSerializer):
    employee_employee_id = serializers.CharField(source="employee.employee_id", read_only=True)
    employee_full_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = AttendanceLog
        fields = [
            "id",
            "employee",
            "employee_employee_id",
            "employee_full_name",
            "check_time",
            "log_type",
            "source",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]