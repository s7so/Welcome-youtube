import pytest
from django.contrib.auth.models import User, Group
from apps.employees.models import Department, Employee
from apps.attendance.models import AttendanceLog, SyncState


@pytest.fixture
def test_user():
    """Create a test user for authentication."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def hr_group():
    """Create HR group for permissions."""
    group, _ = Group.objects.get_or_create(name='HR_Admin')
    return group


@pytest.fixture
def hr_user(test_user, hr_group):
    """Create HR user with proper permissions."""
    test_user.groups.add(hr_group)
    return test_user


@pytest.fixture
def test_department():
    """Create a test department."""
    dept, _ = Department.objects.get_or_create(
        name='Test Department',
        defaults={'description': 'Test department for testing'}
    )
    return dept


@pytest.fixture
def test_employee(test_department):
    """Create a test employee."""
    emp, _ = Employee.objects.get_or_create(
        employee_id='EMP-001',
        defaults={
            'full_name': 'Test Employee',
            'department': test_department,
            'job_title': 'Test Position',
            'is_active': True
        }
    )
    return emp


@pytest.fixture
def attendance_logs(test_employee):
    """Create sample attendance logs for testing."""
    logs = []
    # Create some sample attendance records
    for i in range(5):
        log = AttendanceLog.objects.create(
            employee=test_employee,
            check_time=f'2024-01-0{i+1}T08:00:00Z',
            log_type='IN',
            source='Test Device'
        )
        logs.append(log)
    return logs


@pytest.fixture
def sync_state():
    """Create or get sync state for testing."""
    state, _ = SyncState.objects.get_or_create(
        defaults={
            'last_sync_at': None,
            'last_error_at': None,
            'last_error_message': None
        }
    )
    return state