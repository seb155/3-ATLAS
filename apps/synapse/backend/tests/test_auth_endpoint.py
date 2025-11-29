"""
Tests for authentication endpoints (register, login).
"""

import uuid
import pytest
from app.models.auth import User


class TestAuthRegister:
    """Test user registration endpoint."""

    def test_register_new_user(self, client, db_session):
        """Test successful user registration."""
        unique_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": "securepassword123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == unique_email
        assert data["full_name"] == "Test User"
        assert "id" in data
        # Password should not be in response
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, db_session):
        """Test registration fails with duplicate email."""
        unique_email = f"dup-{uuid.uuid4().hex[:8]}@example.com"

        # First registration
        response1 = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": "password123",
                "full_name": "First User"
            }
        )
        assert response1.status_code == 200

        # Duplicate registration
        response2 = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": "password456",
                "full_name": "Second User"
            }
        )
        assert response2.status_code == 409  # DuplicateError returns 409

    def test_register_without_full_name(self, client, db_session):
        """Test registration without full_name (optional field)."""
        unique_email = f"noname-{uuid.uuid4().hex[:8]}@example.com"
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == unique_email

    def test_register_invalid_email(self, client, db_session):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123"
            }
        )
        # Should fail validation
        assert response.status_code == 422


class TestAuthLogin:
    """Test user login endpoint."""

    @pytest.fixture
    def registered_user(self, client, db_session):
        """Create a registered user for login tests."""
        unique_email = f"login-{uuid.uuid4().hex[:8]}@example.com"
        password = "testpassword123"

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": password,
                "full_name": "Login Test User"
            }
        )
        assert response.status_code == 200

        return {"email": unique_email, "password": password}

    def test_login_success(self, client, registered_user):
        """Test successful login returns access token."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        """Test login fails with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": registered_user["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client, db_session):
        """Test login fails for non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_empty_credentials(self, client, db_session):
        """Test login fails with empty credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "",
                "password": ""
            }
        )
        # Should fail validation or auth
        assert response.status_code in [401, 422]

    def test_token_format(self, client, registered_user):
        """Test access token is properly formatted JWT."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        # JWT has 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3
