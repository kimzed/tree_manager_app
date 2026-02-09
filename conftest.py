import pytest


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }
