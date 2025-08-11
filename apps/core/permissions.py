from rest_framework.permissions import BasePermission, SAFE_METHODS
from .auth import user_has_role, ROLE_HR_ADMIN, ROLE_DEPT_MANAGER, ROLE_AUDITOR


def get_user_scoped_department_id(user):
    if not user.is_authenticated:
        return None
    if user_has_role(user, ROLE_HR_ADMIN):
        return None
    profile = getattr(user, "profile", None)
    if profile and profile.department_id:
        return profile.department_id
    return None


class IsHRAdmin(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, ROLE_HR_ADMIN)


class IsAuditorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return user_has_role(request.user, ROLE_AUDITOR) or user_has_role(request.user, ROLE_HR_ADMIN)
        return user_has_role(request.user, ROLE_HR_ADMIN)


class IsDeptManagerReadOnly(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, ROLE_DEPT_MANAGER) or user_has_role(request.user, ROLE_HR_ADMIN)