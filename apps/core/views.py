from datetime import datetime, timezone
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.models import SyncState, AttendanceLog


class StatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        state = SyncState.objects.filter(key="attendance").first()
        today = now().date()
        today_count = AttendanceLog.objects.filter(check_time__date=today).count()
        return Response({
            "last_sync_time": state.last_sync_time if state else None,
            "last_error_at": state.last_error_at if state else None,
            "last_error_message": state.last_error_message if state else None,
            "today_logs_count": today_count,
        })