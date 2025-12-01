"""FastAPI application tests."""

from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_read_root() -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()


def test_health_check() -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_items() -> None:
    """Test list items endpoint."""
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    assert "items" in response.json()


def test_get_item() -> None:
    """Test get item endpoint."""
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    assert response.json()["item_id"] == 1


def test_create_item() -> None:
    """Test create item endpoint."""
    response = client.post("/api/v1/items?name=test")
    assert response.status_code == 200
    assert response.json()["name"] == "test"


def test_not_found() -> None:
    """Test 404 handler."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert "detail" in response.json()
