import pytest
import csv
import io
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from apps.employees.models import Department, Employee
from apps.core.auth import ROLE_HR_ADMIN


@pytest.mark.integration
@pytest.mark.bulk_upload
class TestBulkUploadIntegration:
    """Integration tests for bulk upload functionality."""
    
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
        
        # Create department
        self.department = Department.objects.create(
            name='IT Department',
            description='Information Technology'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.hr_user)
    
    def create_csv_file(self, data):
        """Helper method to create a CSV file from data."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(data)
        output.seek(0)
        return output
    
    def test_bulk_upload_unauthorized(self):
        """Test bulk upload without authentication."""
        client = APIClient()  # No authentication
        csv_data = [
            ['employee_id', 'full_name', 'department', 'job_title', 'is_active'],
            ['EMP-001', 'Test Employee', 'IT Department', 'Developer', 'true']
        ]
        csv_file = self.create_csv_file(csv_data)
        
        response = client.post('/api/employees/bulk-upload/', {
            'file': ('employees.csv', csv_file, 'text/csv')
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_bulk_upload_success(self):
        """Test successful bulk upload."""
        csv_data = [
            ['employee_id', 'full_name', 'department', 'job_title', 'is_active'],
            ['EMP-001', 'John Doe', 'IT Department', 'Developer', 'true'],
            ['EMP-002', 'Jane Smith', 'IT Department', 'Designer', 'true']
        ]
        csv_file = self.create_csv_file(csv_data)
        
        response = self.client.post('/api/employees/bulk-upload/', {
            'file': ('employees.csv', csv_file, 'text/csv')
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 2
        assert response.data['updated'] == 0
        assert len(response.data['errors']) == 0
        
        # Verify employees were created
        assert Employee.objects.count() == 2
        assert Employee.objects.filter(employee_id='EMP-001').exists()
        assert Employee.objects.filter(employee_id='EMP-002').exists()
    
    def test_bulk_upload_update_existing(self):
        """Test bulk upload updating existing employees."""
        # Create existing employee
        existing_employee = Employee.objects.create(
            employee_id='EMP-001',
            full_name='Old Name',
            department=self.department,
            job_title='Old Position',
            is_active=True
        )
        
        csv_data = [
            ['employee_id', 'full_name', 'department', 'job_title', 'is_active'],
            ['EMP-001', 'New Name', 'IT Department', 'New Position', 'true']
        ]
        csv_file = self.create_csv_file(csv_data)
        
        response = self.client.post('/api/employees/bulk-upload/', {
            'file': ('employees.csv', csv_file, 'text/csv')
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 0
        assert response.data['updated'] == 1
        assert len(response.data['errors']) == 0
        
        # Verify employee was updated
        existing_employee.refresh_from_db()
        assert existing_employee.full_name == 'New Name'
        assert existing_employee.job_title == 'New Position'
    
    def test_bulk_upload_dry_run(self):
        """Test bulk upload with dry run mode."""
        csv_data = [
            ['employee_id', 'full_name', 'department', 'job_title', 'is_active'],
            ['EMP-001', 'Test Employee', 'IT Department', 'Developer', 'true']
        ]
        csv_file = self.create_csv_file(csv_data)
        
        response = self.client.post('/api/employees/bulk-upload/', {
            'file': ('employees.csv', csv_file, 'text/csv'),
            'dry_run': 'true'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['dry_run'] is True
        assert response.data['created'] == 1
        assert response.data['updated'] == 0
        
        # Verify no employees were actually created
        assert Employee.objects.count() == 0
    
    def test_bulk_upload_missing_required_fields(self):
        """Test bulk upload with missing required fields."""
        csv_data = [
            ['employee_id', 'full_name', 'department', 'job_title', 'is_active'],
            ['', 'Test Employee', 'IT Department', 'Developer', 'true'],  # Missing employee_id
            ['EMP-002', '', 'IT Department', 'Designer', 'true']  # Missing full_name
        ]
        csv_file = self.create_csv_file(csv_data)
        
        response = self.client.post('/api/employees/bulk-upload/', {
            'file': ('employees.csv', csv_file, 'text/csv')
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 0
        assert response.data['updated'] == 0
        assert len(response.data['errors']) == 2
        
        # Check error messages
        error_rows = [error['row'] for error in response.data['errors']]
        assert 2 in error_rows  # First data row
        assert 3 in error_rows  # Second data row
    
    def test_bulk_upload_invalid_csv(self):
        """Test bulk upload with invalid CSV format."""
        invalid_data = "This is not a CSV file"
        csv_file = io.StringIO(invalid_data)
        
        response = self.client.post('/api/employees/bulk-upload/', {
            'file': ('employees.csv', csv_file, 'text/csv')
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'invalid CSV file' in response.data['detail']
    
    def test_bulk_upload_missing_file(self):
        """Test bulk upload without file."""
        response = self.client.post('/api/employees/bulk-upload/', {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'file is required' in response.data['detail']
    
    def test_bulk_upload_create_department(self):
        """Test bulk upload creating new department."""
        csv_data = [
            ['employee_id', 'full_name', 'department', 'job_title', 'is_active'],
            ['EMP-001', 'Test Employee', 'New Department', 'Developer', 'true']
        ]
        csv_file = self.create_csv_file(csv_data)
        
        response = self.client.post('/api/employees/bulk-upload/', {
            'file': ('employees.csv', csv_file, 'text/csv')
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 1
        
        # Verify department was created
        new_dept = Department.objects.get(name='New Department')
        assert new_dept is not None
        
        # Verify employee was created with new department
        employee = Employee.objects.get(employee_id='EMP-001')
        assert employee.department == new_dept