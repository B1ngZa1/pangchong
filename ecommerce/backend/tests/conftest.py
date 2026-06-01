"""
Pytest fixtures for backend tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_db():
    """Mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def test_user_data():
    return {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "TestPass1",
        "phone": "13800138001",
        "nickname": "TestUser"
    }


@pytest.fixture
def test_product_data():
    return {
        "name": "测试CPU",
        "slug": "test-cpu-001",
        "description": "测试描述",
        "price": 2999.00,
        "original_price": 3499.00,
        "stock": 10,
        "brand": "Intel",
        "model": "i7-14700K",
        "specs": {"cores": "20", "socket": "LGA1700"},
    }
