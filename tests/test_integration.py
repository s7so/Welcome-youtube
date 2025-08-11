import pytest
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from apps.employees.models import Department, Employee
from apps.attendance.models import AttendanceLog, SyncState
from apps.core.auth import ROLE_HR_ADMIN, ROLE_DEPT_MANAGER


@pytest.mark.integration
@pytest.mark.api
class TestEmployeeIntegration:
    """Integration tests for Employee API endpoints."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        # Create groups
        self.hr_group, _ = Group.objects.get_or_create(name=ROLE_HR_ADMIN)
        self.dept_group, _ = Group.objects.get_or_create(name=ROLE_DEPT_MANAGER)
        
        # Create users
        self.hr_user = User.objects.create_user(
            username='hr_user',
            email='hr@example.com',
            password='testpass123'
        )
        self.hr_user.groups.add(self.hr_group)
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='user@example.com',
            password='testpass123'
        )
        
        # Create department
        self.department = Department.objects.create(
            name='Test Department',
            description='Test department for integration tests'
        )
        
        # Create employee
        self.employee = Employee.objects.create(
            employee_id='EMP-001',
            full_name='Test Employee',
            department=self.department,
            job_title='Test Position',
            is_active=True
        )
        
        self.client = APIClient()
    
    def test_employee_list_unauthorized(self):
        """Test employee list without authentication."""
        response = self.client.get('/api/employees/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_employee_list_authorized(self):
        """Test employee list with HR authentication."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get('/api/employees/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['employee_id'] == 'EMP-001'
    
    def test_employee_detail(self):
        """Test employee detail endpoint."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get(f'/api/employees/{self.employee.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['employee_id'] == 'EMP-001'
        assert response.data['full_name'] == 'Test Employee'
    
    def test_employee_create(self):
        """Test creating a new employee."""
        self.client.force_authenticate(user=self.hr_user)
        data = {
            'employee_id': 'EMP-002',
            'full_name': 'New Employee',
            'department': self.department.id,
            'job_title': 'New Position',
            'is_active': True
        }
        response = self.client.post('/api/employees/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['employee_id'] == 'EMP-002'
        assert Employee.objects.count() == 2
    
    def test_employee_update(self):
        """Test updating an employee."""
        self.client.force_authenticate(user=self.hr_user)
        data = {
            'full_name': 'Updated Employee Name',
            'job_title': 'Updated Position'
        }
        response = self.client.patch(f'/api/employees/{self.employee.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Updated Employee Name'
        
        # Verify database was updated
        self.employee.refresh_from_db()
        assert self.employee.full_name == 'Updated Employee Name'


@pytest.mark.integration
@pytest.mark.api
class TestAttendanceIntegration:
    """Integration tests for Attendance API endpoints."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        # Create groups and users
        self.hr_group, _ = Group.objects.get_or_create(name=ROLE_HR_ADMIN)
        self.hr_user = User.objects.create_user(
            username='hr_user',
            email='hr@example.com',
            password='testpass123'
        )
        self.hr_user.groups.add(self.hr_group)
        
        # Create department and employee
        self.department = Department.objects.create(
            name='Test Department',
            description='Test department'
        )
        self.employee = Employee.objects.create(
            employee_id='EMP-001',
            full_name='Test Employee',
            department=self.department,
            job_title='Test Position',
            is_active=True
        )
        
        # Create attendance logs
        self.attendance_logs = []
        for i in range(3):
            log = AttendanceLog.objects.create(
                employee=self.employee,
                check_time=f'2024-01-0{i+1}T08:00:00Z',
                log_type='IN' if i % 2 == 0 else 'OUT',
                source='Test Device'
            )
            self.attendance_logs.append(log)
        
        self.client = APIClient()
    
    def test_attendance_list_unauthorized(self):
        """Test attendance list without authentication."""
        response = self.client.get('/api/attendance/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_attendance_list_authorized(self):
        """Test attendance list with HR authentication."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get('/api/attendance/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_attendance_filter_by_employee(self):
        """Test filtering attendance by employee."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get(f'/api/attendance/?employee={self.employee.employee_id}')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
        for result in response.data['results']:
            assert result['employee']['employee_id'] == 'EMP-001'
    
    def test_attendance_filter_by_log_type(self):
        """Test filtering attendance by log type."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get('/api/attendance/?log_type=IN')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        for result in response.data['results']:
            assert result['log_type'] == 'IN'


@pytest.mark.integration
@pytest.mark.api
class TestReportsIntegration:
    """Integration tests for Reports API endpoints."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        # Create groups and users
        self.hr_group, _ = Group.objects.get_or_create(name=ROLE_HR_ADMIN)
        self.hr_user = User.objects.create_user(
            username='hr_user',
            email='hr@example.com',
            password='testpass123'
        )
        self.hr_user.groups.add(self.hr_group)
        
        # Create department and employee
        self.department = Department.objects.create(
            name='Test Department',
            description='Test department'
        )
        self.employee = Employee.objects.create(
            employee_id='EMP-001',
            full_name='Test Employee',
            department=self.department,
            job_title='Test Position',
            is_active=True
        )
        
        # Create attendance logs for January 2024
        for day in range(1, 6):  # 5 days
            # Check in
            AttendanceLog.objects.create(
                employee=self.employee,
                check_time=f'2024-01-0{day}T08:00:00Z',
                log_type='IN',
                source='Test Device'
            )
            # Check out
            AttendanceLog.objects.create(
                employee=self.employee,
                check_time=f'2024-01-0{day}T17:00:00Z',
                log_type='OUT',
                source='Test Device'
            )
        
        self.client = APIClient()
    
    def test_monthly_report_unauthorized(self):
        """Test monthly report without authentication."""
        response = self.client.get('/api/reports/monthly/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_monthly_report_authorized(self):
        """Test monthly report with HR authentication."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get('/api/reports/monthly/?year=2024&month=1')
        assert response.status_code == status.HTTP_200_OK
        assert 'employees' in response.data
        assert len(response.data['employees']) == 1
        assert response.data['employees'][0]['employee_id'] == 'EMP-001'
    
    def test_department_monthly_summary(self):
        """Test department monthly summary."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get('/api/reports/department-monthly/?year=2024&month=1')
        assert response.status_code == status.HTTP_200_OK
        assert 'departments' in response.data
        assert len(response.data['departments']) == 1
        assert response.data['departments'][0]['name'] == 'Test Department'
    
    def test_work_hours_report(self):
        """Test work hours report."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get('/api/reports/work-hours/?year=2024&month=1')
        assert response.status_code == status.HTTP_200_OK
        assert 'employees' in response.data
        assert len(response.data['employees']) == 1
        # Should have 5 days * 9 hours = 45 hours
        assert response.data['employees'][0]['total_hours'] == 45.0


@pytest.mark.integration
class TestSyncStateIntegration:
    """Integration tests for SyncState functionality."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        self.sync_state = SyncState.objects.create(
            last_sync_at=None,
            last_error_at=None,
            last_error_message=None
        )
    
    def test_sync_state_creation(self):
        """Test SyncState creation and default values."""
        assert self.sync_state.last_sync_at is None
        assert self.sync_state.last_error_at is None
        assert self.sync_state.last_error_message is None
    
    def test_sync_state_update(self):
        """Test updating SyncState."""
        from django.utils import timezone
        
        now = timezone.now()
        self.sync_state.last_sync_at = now
        self.sync_state.save()
        
        self.sync_state.refresh_from_db()
        assert self.sync_state.last_sync_at == now
    
    def test_sync_state_error_handling(self):
        """Test SyncState error handling."""
        from django.utils import timezone
        
        now = timezone.now()
        error_message = "Test error message"
        
        self.sync_state.last_error_at = now
        self.sync_state.last_error_message = error_message
        self.sync_state.save()
        
        self.sync_state.refresh_from_db()
        assert self.sync_state.last_error_at == now
        assert self.sync_state.last_error_message == error_message