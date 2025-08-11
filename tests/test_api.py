import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestStatusAPI:
    """Test the status API endpoint."""
    
    def test_status_endpoint_unauthorized(self):
        """Test status endpoint without authentication."""
        client = APIClient()
        response = client.get('/api/status')
        assert response.status_code in (401, 403)
    
    def test_status_endpoint_authorized(self, hr_user):
        """Test status endpoint with authentication."""
        client = APIClient()
        client.force_authenticate(user=hr_user)
        response = client.get('/api/status')
        assert response.status_code == 200
        assert 'status' in response.data


@pytest.mark.django_db
class TestEmployeeAPI:
    """Test the employee API endpoints."""
    
    def test_employee_list_unauthorized(self):
        """Test employee list without authentication."""
        client = APIClient()
        response = client.get('/api/employees/')
        assert response.status_code in (401, 403)
    
    def test_employee_list_authorized(self, hr_user, test_employee):
        """Test employee list with authentication."""
        client = APIClient()
        client.force_authenticate(user=hr_user)
        response = client.get('/api/employees/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1
    
    def test_employee_detail(self, hr_user, test_employee):
        """Test employee detail endpoint."""
        client = APIClient()
        client.force_authenticate(user=hr_user)
        response = client.get(f'/api/employees/{test_employee.id}/')
        assert response.status_code == 200
        assert response.data['employee_id'] == test_employee.employee_id


@pytest.mark.django_db
class TestAttendanceAPI:
    """Test the attendance API endpoints."""
    
    def test_attendance_list_unauthorized(self):
        """Test attendance list without authentication."""
        client = APIClient()
        response = client.get('/api/attendance/')
        assert response.status_code in (401, 403)
    
    def test_attendance_list_authorized(self, hr_user, attendance_logs):
        """Test attendance list with authentication."""
        client = APIClient()
        client.force_authenticate(user=hr_user)
        response = client.get('/api/attendance/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 5