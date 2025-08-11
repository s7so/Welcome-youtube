from rest_framework import serializers


class MonthlyEmployeeSummarySerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    employee_identifier = serializers.CharField()
    full_name = serializers.CharField()
    department_name = serializers.CharField(allow_null=True)
    total_logs = serializers.IntegerField()
    first_check_in = serializers.DateTimeField(allow_null=True)
    last_check_out = serializers.DateTimeField(allow_null=True)
    first_seen = serializers.DateTimeField(allow_null=True)
    last_seen = serializers.DateTimeField(allow_null=True)


class MonthlyReportResponseSerializer(serializers.Serializer):
    department = serializers.CharField(allow_null=True)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    count = serializers.IntegerField()
    results = MonthlyEmployeeSummarySerializer(many=True)


class WorkHoursEmployeeSummarySerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    employee_identifier = serializers.CharField()
    full_name = serializers.CharField()
    department_name = serializers.CharField(allow_null=True)
    sessions = serializers.IntegerField()
    total_seconds = serializers.IntegerField()
    total_hours = serializers.FloatField()


class WorkHoursReportResponseSerializer(serializers.Serializer):
    department = serializers.CharField(allow_null=True)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    count = serializers.IntegerField()
    results = WorkHoursEmployeeSummarySerializer(many=True)