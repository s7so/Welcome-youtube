from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.core.auth import ensure_roles_exist, ROLE_HR_ADMIN, ROLE_DEPT_MANAGER, ROLE_AUDITOR
from apps.core.models import UserProfile
from apps.employees.models import Department


class Command(BaseCommand):
    help = "Seed initial roles and optionally assign a user to a role and department."

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, help="Existing username to assign role/profile")
        parser.add_argument("--role", type=str, choices=[ROLE_HR_ADMIN, ROLE_DEPT_MANAGER, ROLE_AUDITOR], help="Role to assign")
        parser.add_argument("--department", type=str, help="Department name to create/use and assign (for dept manager)")

    def handle(self, *args, **options):
        ensure_roles_exist()
        self.stdout.write(self.style.SUCCESS("[OK] Roles ensured"))

        username = options.get("username")
        role = options.get("role")
        dept_name = options.get("department")

        if not username or not role:
            self.stdout.write("No username/role provided. Done.")
            return

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"User '{username}' does not exist"))
            return

        group = Group.objects.get(name=role)
        user.groups.add(group)

        if role == ROLE_DEPT_MANAGER:
            if not dept_name:
                self.stderr.write(self.style.WARNING("--department not provided for dept manager; skipping profile assignment"))
            else:
                dept, _ = Department.objects.get_or_create(name=dept_name)
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.department = dept
                profile.save()
                self.stdout.write(self.style.SUCCESS(f"[OK] Assigned department '{dept.name}' to user '{user.username}'"))

        self.stdout.write(self.style.SUCCESS(f"[OK] Assigned role '{role}' to user '{user.username}'"))