from django.contrib.auth.models import Group

ROLE_HR_ADMIN = "HR_ADMIN"
ROLE_DEPT_MANAGER = "DEPT_MANAGER"
ROLE_AUDITOR = "AUDITOR"


def ensure_roles_exist() -> None:
    for role in [ROLE_HR_ADMIN, ROLE_DEPT_MANAGER, ROLE_AUDITOR]:
        Group.objects.get_or_create(name=role)


def user_has_role(user, role: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=role).exists()