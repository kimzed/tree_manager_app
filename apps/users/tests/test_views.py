import pytest
from django.test import Client
from apps.users.models import CustomUser


@pytest.mark.django_db
def test_successful_registration_redirects(user_data):
    client = Client()
    response = client.post("/users/register/", user_data)
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
def test_duplicate_email_shows_error(user_data):
    CustomUser.objects.create_user(
        username="existing",
        email="test@example.com",
        password="SecurePass123!",
    )
    client = Client()
    response = client.post("/users/register/", user_data)
    assert response.status_code == 200
    assert b"already exists" in response.content


@pytest.mark.django_db
def test_weak_password_shows_error():
    client = Client()
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "123",
        "password2": "123",
    }
    response = client.post("/users/register/", data)
    assert response.status_code == 200
    assert b"password" in response.content.lower()
