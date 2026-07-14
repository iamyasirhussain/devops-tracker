"""
Tests for the DevOps Learning Tracker.
FastAPI's TestClient calls the app directly — no server needed.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_homepage_loads():
    """The dining room should open."""
    response = client.get("/")
    assert response.status_code == 200
    assert "DevOps Learning Tracker" in response.text


def test_can_add_and_list_items():
    """Add an item, then check it comes back in the list."""
    client.post("/api/items", json={"text": "Learn Kubernetes"})
    response = client.get("/api/items")
    assert response.status_code == 200
    assert any(item["text"] == "Learn Kubernetes" for item in response.json())


def test_metrics_endpoint_works():
    """The tally sheet should be readable and contain our custom metric."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "app_requests_total" in response.text
