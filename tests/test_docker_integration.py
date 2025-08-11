import pytest
import os
from django.test import TestCase
from django.contrib.auth.models import User, Group
from apps.employees.models import Department, Employee
from apps.attendance.models import AttendanceLog, SyncState
from apps.core.auth import ROLE_HR_ADMIN


@pytest.mark.integration
class TestDockerEnvironment(TestCase):
    """Test to verify Docker test environment is properly configured."""
    
    def test_database_connection(self):
        """Test that database connection is working."""
        # Try to create a simple object
        dept = Department.objects.create(
            name='Test Department',
            description='Test department for Docker environment'
        )
        self.assertIsNotNone(dept.id)
        
        # Verify it can be retrieved
        retrieved_dept = Department.objects.get(id=dept.id)
        self.assertEqual(retrieved_dept.name, 'Test Department')
    
    def test_redis_connection(self):
        """Test that Redis connection is working (if configured)."""
        try:
            from django.core.cache import cache
            cache.set('test_key', 'test_value', 10)
            value = cache.get('test_key')
            self.assertEqual(value, 'test_value')
        except Exception as e:
            self.skipTest(f"Redis not available: {e}")
    
    def test_environment_variables(self):
        """Test that required environment variables are set."""
        # Check that we're using test database
        from django.conf import settings
        self.assertIn('test', settings.DATABASES['default']['NAME'].lower())
    
    def test_test_superuser_exists(self):
        """Test that test superuser was created."""
        try:
            test_admin = User.objects.get(username='testadmin')
            self.assertTrue(test_admin.is_superuser)
        except User.DoesNotExist:
            self.skipTest("Test superuser not found - run setup first")
    
    def test_hr_group_exists(self):
        """Test that HR group exists."""
        hr_group = Group.objects.get(name=ROLE_HR_ADMIN)
        self.assertIsNotNone(hr_group)
    
    def test_can_create_employee(self):
        """Test that we can create employees."""
        dept = Department.objects.create(
            name='Test Department',
            description='Test department'
        )
        
        employee = Employee.objects.create(
            employee_id='EMP-001',
            full_name='Test Employee',
            department=dept,
            job_title='Test Position',
            is_active=True
        )
        
        self.assertIsNotNone(employee.id)
        self.assertEqual(employee.employee_id, 'EMP-001')
    
    def test_can_create_attendance_log(self):
        """Test that we can create attendance logs."""
        dept = Department.objects.create(
            name='Test Department',
            description='Test department'
        )
        
        employee = Employee.objects.create(
            employee_id='EMP-001',
            full_name='Test Employee',
            department=dept,
            job_title='Test Position',
            is_active=True
        )
        
        log = AttendanceLog.objects.create(
            employee=employee,
            check_time='2024-01-01T08:00:00Z',
            log_type='IN',
            source='Test Device'
        )
        
        self.assertIsNotNone(log.id)
        self.assertEqual(log.employee, employee)
    
    def test_sync_state_creation(self):
        """Test that SyncState can be created."""
        sync_state = SyncState.objects.create()
        self.assertIsNotNone(sync_state.id)
        self.assertIsNone(sync_state.last_sync_at)
        self.assertIsNone(sync_state.last_error_at)


@pytest.mark.integration
class TestDockerPerformance(TestCase):
    """Test performance characteristics in Docker environment."""
    
    def test_bulk_employee_creation(self):
        """Test creating multiple employees efficiently."""
        dept = Department.objects.create(
            name='Test Department',
            description='Test department'
        )
        
        # Create 100 employees
        employees = []
        for i in range(100):
            employee = Employee(
                employee_id=f'EMP-{i:03d}',
                full_name=f'Employee {i}',
                department=dept,
                job_title=f'Position {i}',
                is_active=True
            )
            employees.append(employee)
        
        # Bulk create
        Employee.objects.bulk_create(employees)
        
        # Verify all were created
        self.assertEqual(Employee.objects.count(), 100)
    
    def test_bulk_attendance_creation(self):
        """Test creating multiple attendance logs efficiently."""
        dept = Department.objects.create(
            name='Test Department',
            description='Test department'
        )
        
        employee = Employee.objects.create(
            employee_id='EMP-001',
            full_name='Test Employee',
            department=dept,
            job_title='Test Position',
            is_active=True
        )
        
        # Create 1000 attendance logs
        logs = []
        for i in range(1000):
            log = AttendanceLog(
                employee=employee,
                check_time=f'2024-01-01T{(i % 24):02d}:{(i % 60):02d}:00Z',
                log_type='IN' if i % 2 == 0 else 'OUT',
                source='Test Device'
            )
            logs.append(log)
        
        # Bulk create
        AttendanceLog.objects.bulk_create(logs)
        
        # Verify all were created
        self.assertEqual(AttendanceLog.objects.count(), 1000)
    
    def test_database_query_performance(self):
        """Test that database queries are reasonably fast."""
        import time
        
        # Create test data
        dept = Department.objects.create(
            name='Test Department',
            description='Test department'
        )
        
        employees = []
        for i in range(50):
            employee = Employee.objects.create(
                employee_id=f'EMP-{i:03d}',
                full_name=f'Employee {i}',
                department=dept,
                job_title=f'Position {i}',
                is_active=True
            )
            employees.append(employee)
        
        # Test query performance
        start_time = time.time()
        employee_list = list(Employee.objects.all())
        query_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 1 second)
        self.assertLess(query_time, 1.0)
        self.assertEqual(len(employee_list), 50)