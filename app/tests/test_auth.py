"""
Test JWT + refresh
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "visitor"
        }
    )
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == "test@example.com"


def test_login():
    """Test user login"""
    # First register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "testpass123",
            "role": "visitor"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_refresh_token():
    """Test token refresh"""
    # Register and login first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@example.com",
            "username": "refreshuser",
            "password": "testpass123",
            "role": "visitor"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "refreshuser",
            "password": "testpass123"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh access token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

