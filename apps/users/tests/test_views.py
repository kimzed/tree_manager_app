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


@pytest.mark.django_db
def test_successful_login_redirects():
    CustomUser.objects.create_user(
        username="loginuser",
        email="login@example.com",
        password="SecurePass123!",
    )
    client = Client()
    response = client.post(
        "/users/login/",
        {"username": "loginuser", "password": "SecurePass123!"},
    )
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
def test_invalid_credentials_shows_error():
    client = Client()
    response = client.post(
        "/users/login/",
        {"username": "nobody", "password": "wrong"},
    )
    assert response.status_code == 200
    assert b"please enter a correct username" in response.content.lower()


@pytest.mark.django_db
def test_logout_redirects_and_terminates_session():
    CustomUser.objects.create_user(
        username="logoutuser",
        email="logout@example.com",
        password="SecurePass123!",
    )
    client = Client()
    client.login(username="logoutuser", password="SecurePass123!")
    response = client.post("/users/logout/")
    assert response.status_code == 302
    assert response.url == "/"
    landing = client.get("/")
    assert b"logoutuser" not in landing.content


@pytest.mark.django_db
def test_login_page_renders():
    client = Client()
    response = client.get("/users/login/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_rejects_get_request():
    client = Client()
    response = client.get("/users/logout/")
    assert response.status_code == 405
