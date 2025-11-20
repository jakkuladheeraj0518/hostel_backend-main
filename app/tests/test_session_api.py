"""
Test session switching APIs
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_switch_session():
    """Test switching active hostel session"""
    pass


def test_get_active_session():
    """Test getting active session"""
    pass


def test_recent_sessions():
    """Test getting recent sessions"""
    pass

