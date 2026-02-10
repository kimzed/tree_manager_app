import pytest
from apps.users.models import CustomUser


@pytest.fixture
def new_user():
    return CustomUser.objects.create_user(
        username="profileuser",
        email="profile@example.com",
        password="SecurePass123!",
    )


@pytest.mark.django_db
def test_create_user_with_email():
    user = CustomUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="SecurePass123!",
    )
    assert user.email == "test@example.com"


@pytest.mark.django_db
def test_new_user_goals_defaults_to_empty_list(new_user):
    assert new_user.goals == []


@pytest.mark.django_db
def test_new_user_maintenance_level_defaults_to_empty(new_user):
    assert new_user.maintenance_level == ""


@pytest.mark.django_db
def test_new_user_experience_level_defaults_to_empty(new_user):
    assert new_user.experience_level == ""


@pytest.mark.django_db
def test_new_user_profile_completed_defaults_to_false(new_user):
    assert new_user.profile_completed is False
