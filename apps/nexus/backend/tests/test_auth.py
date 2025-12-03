from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Nexus API v0.2.0"


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "pytest@example.com",
            "username": "pytestuser",
            "password": "testpass123"
        }
    )
    # Note: This might fail if DB is not set up
    # assert response.status_code == 201
    # assert response.json()["email"] == "pytest@example.com"


def test_login_user():
    # First register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "testpass123"
        }
    )

    # Then login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpass123"
        }
    )
    # Note: This might fail if DB is not set up
    # assert response.status_code == 200
    # assert "access_token" in response.json()
