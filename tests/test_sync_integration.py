import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User, Group
from django.utils import timezone
from apps.employees.models import Department, Employee
from apps.attendance.models import AttendanceLog, SyncState
from apps.attendance.tasks.sync import run_sync_job
from apps.core.auth import ROLE_HR_ADMIN


@pytest.mark.integration
@pytest.mark.sync
class TestSyncIntegration:
    """Integration tests for sync functionality."""
    
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
        
        # Create sync state
        self.sync_state = SyncState.objects.create(
            last_sync_at=None,
            last_error_at=None,
            last_error_message=None
        )
    
    @patch('apps.attendance.tasks.sync.FingerTecAdapter')
    @patch('apps.attendance.tasks.sync.alerter')
    def test_sync_job_success(self, mock_alerter, mock_adapter_class):
        """Test successful sync job execution."""
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        
        # Mock attendance data from device
        mock_attendance_data = [
            {
                'employee_id': 'EMP-001',
                'timestamp': '2024-01-01T08:00:00Z',
                'log_type': 'IN',
                'source': 'Test Device'
            },
            {
                'employee_id': 'EMP-001',
                'timestamp': '2024-01-01T17:00:00Z',
                'log_type': 'OUT',
                'source': 'Test Device'
            }
        ]
        mock_adapter.fetch_attendance_logs.return_value = mock_attendance_data
        
        # Run sync job
        result = run_sync_job()
        
        # Verify adapter was called
        mock_adapter.fetch_attendance_logs.assert_called_once()
        
        # Verify attendance logs were created
        assert AttendanceLog.objects.count() == 2
        
        # Verify sync state was updated
        self.sync_state.refresh_from_db()
        assert self.sync_state.last_sync_at is not None
        assert self.sync_state.last_error_at is None
        assert self.sync_state.last_error_message is None
        
        # Verify alerter was not called (no errors)
        mock_alerter.send_alert.assert_not_called()
    
    @patch('apps.attendance.tasks.sync.FingerTecAdapter')
    @patch('apps.attendance.tasks.sync.alerter')
    def test_sync_job_with_unknown_employee(self, mock_alerter, mock_adapter_class):
        """Test sync job with unknown employee ID."""
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        
        # Mock attendance data with unknown employee
        mock_attendance_data = [
            {
                'employee_id': 'UNKNOWN-001',
                'timestamp': '2024-01-01T08:00:00Z',
                'log_type': 'IN',
                'source': 'Test Device'
            }
        ]
        mock_adapter.fetch_attendance_logs.return_value = mock_attendance_data
        
        # Run sync job
        result = run_sync_job()
        
        # Verify no attendance logs were created for unknown employee
        assert AttendanceLog.objects.count() == 0
        
        # Verify sync state was updated
        self.sync_state.refresh_from_db()
        assert self.sync_state.last_sync_at is not None
    
    @patch('apps.attendance.tasks.sync.FingerTecAdapter')
    @patch('apps.attendance.tasks.sync.alerter')
    def test_sync_job_adapter_error(self, mock_alerter, mock_adapter_class):
        """Test sync job when adapter raises an error."""
        # Mock adapter to raise an error
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        mock_adapter.fetch_attendance_logs.side_effect = Exception("Connection failed")
        
        # Run sync job
        result = run_sync_job()
        
        # Verify no attendance logs were created
        assert AttendanceLog.objects.count() == 0
        
        # Verify sync state was updated with error
        self.sync_state.refresh_from_db()
        assert self.sync_state.last_error_at is not None
        assert self.sync_state.last_error_message is not None
        
        # Verify alerter was called
        mock_alerter.send_alert.assert_called_once()
    
    @patch('apps.attendance.tasks.sync.FingerTecAdapter')
    @patch('apps.attendance.tasks.sync.alerter')
    def test_sync_job_duplicate_logs(self, mock_alerter, mock_adapter_class):
        """Test sync job with duplicate attendance logs."""
        # Create existing attendance log
        existing_log = AttendanceLog.objects.create(
            employee=self.employee,
            check_time='2024-01-01T08:00:00Z',
            log_type='IN',
            source='Test Device'
        )
        
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        
        # Mock attendance data with duplicate
        mock_attendance_data = [
            {
                'employee_id': 'EMP-001',
                'timestamp': '2024-01-01T08:00:00Z',  # Same as existing
                'log_type': 'IN',
                'source': 'Test Device'
            }
        ]
        mock_adapter.fetch_attendance_logs.return_value = mock_attendance_data
        
        # Run sync job
        result = run_sync_job()
        
        # Verify no new attendance logs were created (duplicate prevention)
        assert AttendanceLog.objects.count() == 1
        
        # Verify sync state was updated
        self.sync_state.refresh_from_db()
        assert self.sync_state.last_sync_at is not None
    
    def test_sync_state_initialization(self):
        """Test SyncState initialization and defaults."""
        # Create new sync state
        new_sync_state = SyncState.objects.create()
        
        assert new_sync_state.last_sync_at is None
        assert new_sync_state.last_error_at is None
        assert new_sync_state.last_error_message is None
    
    def test_sync_state_error_tracking(self):
        """Test SyncState error tracking functionality."""
        now = timezone.now()
        error_message = "Test error message"
        
        # Update sync state with error
        self.sync_state.last_error_at = now
        self.sync_state.last_error_message = error_message
        self.sync_state.save()
        
        # Verify error was tracked
        self.sync_state.refresh_from_db()
        assert self.sync_state.last_error_at == now
        assert self.sync_state.last_error_message == error_message
        
        # Test clearing error
        self.sync_state.last_error_at = None
        self.sync_state.last_error_message = None
        self.sync_state.save()
        
        self.sync_state.refresh_from_db()
        assert self.sync_state.last_error_at is None
        assert self.sync_state.last_error_message is None
    
    @patch('apps.attendance.tasks.sync.FingerTecAdapter')
    @patch('apps.attendance.tasks.sync.alerter')
    def test_sync_job_with_multiple_employees(self, mock_alerter, mock_adapter_class):
        """Test sync job with multiple employees."""
        # Create additional employee
        employee2 = Employee.objects.create(
            employee_id='EMP-002',
            full_name='Test Employee 2',
            department=self.department,
            job_title='Test Position 2',
            is_active=True
        )
        
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        
        # Mock attendance data for multiple employees
        mock_attendance_data = [
            {
                'employee_id': 'EMP-001',
                'timestamp': '2024-01-01T08:00:00Z',
                'log_type': 'IN',
                'source': 'Test Device'
            },
            {
                'employee_id': 'EMP-002',
                'timestamp': '2024-01-01T08:30:00Z',
                'log_type': 'IN',
                'source': 'Test Device'
            }
        ]
        mock_adapter.fetch_attendance_logs.return_value = mock_attendance_data
        
        # Run sync job
        result = run_sync_job()
        
        # Verify attendance logs were created for both employees
        assert AttendanceLog.objects.count() == 2
        assert AttendanceLog.objects.filter(employee=self.employee).count() == 1
        assert AttendanceLog.objects.filter(employee=employee2).count() == 1