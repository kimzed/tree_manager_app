import pytest
from django.test import Client

from apps.users.models import CustomUser

VALID_PROFILE_DATA = {
    "goals": ["fruit", "shade"],
    "maintenance_level": "low",
    "experience_level": "beginner",
}


@pytest.fixture
def user_with_incomplete_profile():
    return CustomUser.objects.create_user(
        username="newuser",
        email="new@example.com",
        password="SecurePass123!",
        profile_completed=False,
    )


@pytest.fixture
def authenticated_client(user_with_incomplete_profile):
    client = Client()
    client.login(username="newuser", password="SecurePass123!")
    return client


@pytest.mark.django_db
def test_profile_setup_renders_for_authenticated_user(authenticated_client):
    response = authenticated_client.get("/users/profile/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_setup_redirects_anonymous_user():
    client = Client()
    response = client.get("/users/profile/")
    assert "/users/login/" in response.url


@pytest.mark.django_db
def test_valid_profile_submission_redirects_to_landing(authenticated_client):
    response = authenticated_client.post("/users/profile/", VALID_PROFILE_DATA)
    assert response.url == "/"


@pytest.mark.django_db
def test_valid_profile_submission_saves_goals(
    authenticated_client, user_with_incomplete_profile
):
    authenticated_client.post("/users/profile/", VALID_PROFILE_DATA)
    user_with_incomplete_profile.refresh_from_db()
    assert user_with_incomplete_profile.goals == ["fruit", "shade"]


@pytest.mark.django_db
def test_valid_profile_submission_saves_maintenance_level(
    authenticated_client, user_with_incomplete_profile
):
    authenticated_client.post("/users/profile/", VALID_PROFILE_DATA)
    user_with_incomplete_profile.refresh_from_db()
    assert user_with_incomplete_profile.maintenance_level == "low"


@pytest.mark.django_db
def test_valid_profile_submission_saves_experience_level(
    authenticated_client, user_with_incomplete_profile
):
    authenticated_client.post("/users/profile/", VALID_PROFILE_DATA)
    user_with_incomplete_profile.refresh_from_db()
    assert user_with_incomplete_profile.experience_level == "beginner"


@pytest.mark.django_db
def test_valid_profile_submission_sets_profile_completed(
    authenticated_client, user_with_incomplete_profile
):
    authenticated_client.post("/users/profile/", VALID_PROFILE_DATA)
    user_with_incomplete_profile.refresh_from_db()
    assert user_with_incomplete_profile.profile_completed is True
