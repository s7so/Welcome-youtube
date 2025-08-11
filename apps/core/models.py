from django.conf import settings
from django.db import models
from apps.employees.models import Department


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self) -> str:
        return f"Profile({self.user.username})"