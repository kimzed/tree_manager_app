import json

import pytest
from unittest.mock import patch
from django.test import Client

from apps.parcels.models import Parcel
from apps.parcels.services.geocoding import GeocodingError

SAMPLE_POLYGON = {
    "type": "Polygon",
    "coordinates": [[[2.35, 48.85], [2.36, 48.85], [2.36, 48.86], [2.35, 48.85]]],
}


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


@pytest.mark.django_db
def test_parcel_save_creates_parcel_for_authenticated_user(user):
    client = Client()
    client.force_login(user)
    response = client.post("/parcels/save/", {
        "polygon": json.dumps(SAMPLE_POLYGON),
        "area_m2": "450.50",
        "latitude": "48.85",
        "longitude": "2.35",
    })
    assert b"Parcel saved!" in response.content


@pytest.mark.django_db
def test_parcel_save_requires_login():
    client = Client()
    response = client.post("/parcels/save/", {
        "polygon": json.dumps(SAMPLE_POLYGON),
        "area_m2": "450.50",
    })
    assert response.status_code == 302


@pytest.mark.django_db
def test_parcel_save_rejects_get_request(user):
    client = Client()
    client.force_login(user)
    response = client.get("/parcels/save/")
    assert response.status_code == 405


@pytest.mark.django_db
def test_parcel_save_missing_polygon_returns_error_partial(user):
    client = Client()
    client.force_login(user)
    response = client.post("/parcels/save/", {"area_m2": "450.50"})
    assert b"Could not save parcel" in response.content


@pytest.mark.django_db
def test_parcel_save_stores_correct_polygon(user):
    client = Client()
    client.force_login(user)
    client.post("/parcels/save/", {
        "polygon": json.dumps(SAMPLE_POLYGON),
        "area_m2": "450.50",
        "latitude": "48.85",
        "longitude": "2.35",
    })
    parcel = Parcel.objects.get(user=user)
    assert parcel.polygon == SAMPLE_POLYGON


@pytest.mark.django_db
def test_parcel_save_stores_correct_area(user):
    client = Client()
    client.force_login(user)
    client.post("/parcels/save/", {
        "polygon": json.dumps(SAMPLE_POLYGON),
        "area_m2": "450.50",
        "latitude": "48.85",
        "longitude": "2.35",
    })
    parcel = Parcel.objects.get(user=user)
    assert parcel.area_m2 == 450.50


@pytest.mark.django_db
def test_parcel_save_invalid_latitude_returns_error_partial(user):
    client = Client()
    client.force_login(user)
    response = client.post("/parcels/save/", {
        "polygon": json.dumps(SAMPLE_POLYGON),
        "area_m2": "450.50",
        "latitude": "not-a-number",
        "longitude": "2.35",
    })
    assert b"Could not save parcel" in response.content


@pytest.mark.django_db
def test_parcel_save_invalid_geojson_structure_returns_error_partial(user):
    client = Client()
    client.force_login(user)
    response = client.post("/parcels/save/", {
        "polygon": json.dumps({"foo": "bar"}),
        "area_m2": "450.50",
    })
    assert b"Could not save parcel" in response.content
