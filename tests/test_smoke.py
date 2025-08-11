import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_status_endpoint_client(client):
    # Without auth, should be 403
    resp = client.get("/api/status")
    assert resp.status_code in (401, 403)