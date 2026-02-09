import pytest
from apps.users.models import CustomUser


@pytest.mark.django_db
def test_create_user_with_email():
    user = CustomUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="SecurePass123!",
    )
    assert user.email == "test@example.com"
