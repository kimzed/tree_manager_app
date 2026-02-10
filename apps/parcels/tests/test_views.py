import pytest
from unittest.mock import patch
from django.test import Client

from apps.parcels.services.geocoding import GeocodingError


@pytest.mark.django_db
def test_parcel_create_requires_login():
    client = Client()
    response = client.get("/parcels/create/")
    assert response.status_code == 302 and "/users/login/" in response.url


@pytest.mark.django_db
def test_parcel_create_returns_200_for_authenticated_user(user):
    client = Client()
    client.force_login(user)
    response = client.get("/parcels/create/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_geocode_view_valid_address_returns_result_partial(user):
    client = Client()
    client.force_login(user)
    mock_result = {"lat": 48.8566, "lon": 2.3522, "display_name": "Paris, France"}
    with patch("apps.parcels.views.geocode_address", return_value=mock_result):
        response = client.post("/parcels/geocode/", {"address": "Paris"})
    assert b"Paris, France" in response.content


@pytest.mark.django_db
def test_geocode_view_unfound_address_returns_error_partial(user):
    client = Client()
    client.force_login(user)
    with patch("apps.parcels.views.geocode_address", return_value=None):
        response = client.post("/parcels/geocode/", {"address": "nonexistent"})
    assert b"Address not found" in response.content


@pytest.mark.django_db
def test_geocode_view_rejects_get_request(user):
    client = Client()
    client.force_login(user)
    response = client.get("/parcels/geocode/")
    assert response.status_code == 405


@pytest.mark.django_db
def test_geocode_view_empty_address_returns_error_partial(user):
    client = Client()
    client.force_login(user)
    response = client.post("/parcels/geocode/", {"address": "  "})
    assert b"Address not found" in response.content


@pytest.mark.django_db
def test_geocode_view_service_error_returns_error_partial(user):
    client = Client()
    client.force_login(user)
    with patch("apps.parcels.views.geocode_address", side_effect=GeocodingError("timeout")):
        response = client.post("/parcels/geocode/", {"address": "Paris"})
    assert b"Address not found" in response.content
