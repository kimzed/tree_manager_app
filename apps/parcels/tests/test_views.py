import json

import pytest
from unittest.mock import MagicMock, patch
from django.test import Client

from apps.parcels.models import Parcel
from apps.parcels.services.geocoding import GeocodingError
from apps.parcels.services.koppen import KoppenError
from apps.parcels.services.macrostrat import MacrostratError
from apps.parcels.services.soilgrids import SoilGridsError

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


# --- Story 2.3: Parcel list view tests ---


@pytest.mark.django_db
def test_parcel_list_requires_login():
    client = Client()
    response = client.get("/parcels/")
    assert response.status_code == 302 and "/users/login/" in response.url


@pytest.mark.django_db
def test_parcel_list_shows_own_parcels(user):
    Parcel.objects.create(user=user, name="My Parcel", polygon=SAMPLE_POLYGON, area_m2=100.0)
    client = Client()
    client.force_login(user)
    response = client.get("/parcels/")
    assert b"My Parcel" in response.content


@pytest.mark.django_db
def test_parcel_list_excludes_other_users_parcels(user):
    from django.contrib.auth import get_user_model
    other_user = get_user_model().objects.create_user(
        username="otheruser", email="other@example.com", password="SecurePass123!",
    )
    Parcel.objects.create(user=other_user, name="Other Parcel", polygon=SAMPLE_POLYGON, area_m2=200.0)
    client = Client()
    client.force_login(user)
    response = client.get("/parcels/")
    assert b"Other Parcel" not in response.content


# --- Story 2.3: Parcel detail view tests ---


@pytest.mark.django_db
def test_parcel_detail_returns_correct_parcel_for_owner(user):
    parcel = Parcel.objects.create(user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=300.0)
    client = Client()
    client.force_login(user)
    response = client.get(f"/parcels/{parcel.pk}/")
    assert response.status_code == 200
    assert b"Garden" in response.content


@pytest.mark.django_db
def test_parcel_detail_returns_404_for_other_users_parcel(user):
    from django.contrib.auth import get_user_model
    other_user = get_user_model().objects.create_user(
        username="otheruser", email="other@example.com", password="SecurePass123!",
    )
    parcel = Parcel.objects.create(user=other_user, name="Secret", polygon=SAMPLE_POLYGON, area_m2=100.0)
    client = Client()
    client.force_login(user)
    response = client.get(f"/parcels/{parcel.pk}/")
    assert response.status_code == 404


# --- Story 2.3: Parcel edit view tests ---


@pytest.mark.django_db
def test_parcel_edit_loads_parcel_data_for_owner(user):
    parcel = Parcel.objects.create(user=user, name="Editable", polygon=SAMPLE_POLYGON, area_m2=500.0)
    client = Client()
    client.force_login(user)
    response = client.get(f"/parcels/{parcel.pk}/edit/")
    assert response.status_code == 200
    assert b"Editable" in response.content


@pytest.mark.django_db
def test_parcel_edit_returns_404_for_other_users_parcel(user):
    from django.contrib.auth import get_user_model
    other_user = get_user_model().objects.create_user(
        username="otheruser", email="other@example.com", password="SecurePass123!",
    )
    parcel = Parcel.objects.create(user=other_user, name="Secret", polygon=SAMPLE_POLYGON, area_m2=100.0)
    client = Client()
    client.force_login(user)
    response = client.get(f"/parcels/{parcel.pk}/edit/")
    assert response.status_code == 404


# --- Story 2.3: Parcel update view tests ---


@pytest.mark.django_db
def test_parcel_update_saves_new_polygon_for_owner(user):
    parcel = Parcel.objects.create(user=user, polygon=SAMPLE_POLYGON, area_m2=100.0)
    new_polygon = {
        "type": "Polygon",
        "coordinates": [[[2.37, 48.87], [2.38, 48.87], [2.38, 48.88], [2.37, 48.87]]],
    }
    client = Client()
    client.force_login(user)
    client.post(f"/parcels/{parcel.pk}/update/", {
        "polygon": json.dumps(new_polygon),
        "area_m2": "750.00",
    })
    parcel.refresh_from_db()
    assert parcel.polygon == new_polygon


@pytest.mark.django_db
def test_parcel_update_returns_404_for_other_users_parcel(user):
    from django.contrib.auth import get_user_model
    other_user = get_user_model().objects.create_user(
        username="otheruser", email="other@example.com", password="SecurePass123!",
    )
    parcel = Parcel.objects.create(user=other_user, polygon=SAMPLE_POLYGON, area_m2=100.0)
    client = Client()
    client.force_login(user)
    response = client.post(f"/parcels/{parcel.pk}/update/", {
        "polygon": json.dumps(SAMPLE_POLYGON),
        "area_m2": "500.00",
    })
    assert response.status_code == 404


@pytest.mark.django_db
def test_parcel_update_rejects_get_request(user):
    parcel = Parcel.objects.create(user=user, polygon=SAMPLE_POLYGON, area_m2=100.0)
    client = Client()
    client.force_login(user)
    response = client.get(f"/parcels/{parcel.pk}/update/")
    assert response.status_code == 405


@pytest.mark.django_db
def test_parcel_update_missing_polygon_returns_error_partial(user):
    parcel = Parcel.objects.create(user=user, polygon=SAMPLE_POLYGON, area_m2=100.0)
    client = Client()
    client.force_login(user)
    response = client.post(f"/parcels/{parcel.pk}/update/", {"area_m2": "500.00"})
    assert b"Could not save parcel" in response.content


# --- Story 2.3: Multiple parcels test ---


@pytest.mark.django_db
def test_creating_multiple_parcels_for_same_user(user):
    client = Client()
    client.force_login(user)
    client.post("/parcels/save/", {
        "polygon": json.dumps(SAMPLE_POLYGON),
        "area_m2": "100.00",
        "latitude": "48.85",
        "longitude": "2.35",
    })
    client.post("/parcels/save/", {
        "polygon": json.dumps(SAMPLE_POLYGON),
        "area_m2": "200.00",
        "latitude": "48.86",
        "longitude": "2.36",
    })
    assert Parcel.objects.filter(user=user).count() == 2


# --- Story 2.4: Parcel analyze view tests ---


@pytest.mark.django_db
def test_parcel_analyze_stores_climate_zone(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    with patch("apps.parcels.views.get_koppen_zone", return_value="Cfb - Oceanic"):
        client.post(f"/parcels/{parcel.pk}/analyze/")
    parcel.refresh_from_db()
    assert parcel.climate_zone == "Cfb - Oceanic"


@pytest.mark.django_db
def test_parcel_analyze_returns_result_partial(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    with patch("apps.parcels.views.get_koppen_zone", return_value="Cfb - Oceanic"):
        response = client.post(f"/parcels/{parcel.pk}/analyze/")
    assert b"Cfb - Oceanic" in response.content


@pytest.mark.django_db
def test_parcel_analyze_returns_error_partial_when_no_location(user):
    parcel = Parcel.objects.create(
        user=user, name="No Location", polygon=SAMPLE_POLYGON, area_m2=100.0,
    )
    client = Client()
    client.force_login(user)
    response = client.post(f"/parcels/{parcel.pk}/analyze/")
    assert b"Location data is required" in response.content


@pytest.mark.django_db
def test_parcel_analyze_returns_error_partial_on_koppen_error(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    with patch("apps.parcels.views.get_koppen_zone", side_effect=KoppenError("GeoTIFF missing")):
        response = client.post(f"/parcels/{parcel.pk}/analyze/")
    assert b"GeoTIFF missing" in response.content


@pytest.mark.django_db
def test_parcel_analyze_requires_login():
    client = Client()
    response = client.post("/parcels/1/analyze/")
    assert response.status_code == 302 and "/users/login/" in response.url


@pytest.mark.django_db
def test_parcel_analyze_returns_404_for_other_users_parcel(user):
    from django.contrib.auth import get_user_model
    other_user = get_user_model().objects.create_user(
        username="otheruser", email="other@example.com", password="SecurePass123!",
    )
    parcel = Parcel.objects.create(
        user=other_user, name="Secret", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    response = client.post(f"/parcels/{parcel.pk}/analyze/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_parcel_analyze_rejects_get_request(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    response = client.get(f"/parcels/{parcel.pk}/analyze/")
    assert response.status_code == 405


# --- Story 2.5: Soil analyze view tests ---


@pytest.mark.django_db
def test_soil_analyze_stores_soil_ph_on_parcel(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    mock_soil = MagicMock(ph=6.5, drainage="Moderately drained", approximate=False)
    with patch("apps.parcels.views.get_soil_data", return_value=mock_soil):
        client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    parcel.refresh_from_db()
    assert parcel.soil_ph == 6.5


@pytest.mark.django_db
def test_soil_analyze_stores_soil_drainage_on_parcel(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    mock_soil = MagicMock(ph=6.5, drainage="Moderately drained", approximate=False)
    with patch("apps.parcels.views.get_soil_data", return_value=mock_soil):
        client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    parcel.refresh_from_db()
    assert parcel.soil_drainage == "Moderately drained"


@pytest.mark.django_db
def test_soil_analyze_returns_result_partial(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    mock_soil = MagicMock(ph=6.5, drainage="Moderately drained", approximate=False)
    with patch("apps.parcels.views.get_soil_data", return_value=mock_soil):
        response = client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    assert b"Moderately drained" in response.content


@pytest.mark.django_db
def test_soil_analyze_returns_error_partial_when_no_location(user):
    parcel = Parcel.objects.create(
        user=user, name="No Location", polygon=SAMPLE_POLYGON, area_m2=100.0,
    )
    client = Client()
    client.force_login(user)
    response = client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    assert b"Location data is required" in response.content


@pytest.mark.django_db
def test_soil_analyze_requires_login():
    client = Client()
    response = client.post("/parcels/1/soil-analyze/")
    assert response.status_code == 302 and "/users/login/" in response.url


@pytest.mark.django_db
def test_soil_analyze_returns_404_for_other_users_parcel(user):
    from django.contrib.auth import get_user_model
    other_user = get_user_model().objects.create_user(
        username="otheruser", email="other@example.com", password="SecurePass123!",
    )
    parcel = Parcel.objects.create(
        user=other_user, name="Secret", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    response = client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_soil_analyze_rejects_get_request(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    response = client.get(f"/parcels/{parcel.pk}/soil-analyze/")
    assert response.status_code == 405


# --- Story 2.5: Soil skip view tests ---


@pytest.mark.django_db
def test_soil_skip_returns_caveat_partial(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    response = client.post(f"/parcels/{parcel.pk}/soil-skip/")
    assert b"Soil data unavailable" in response.content


# --- Story 2.5b: Macrostrat fallback view tests ---


@pytest.mark.django_db
def test_soil_analyze_sets_source_measured_when_soilgrids_succeeds(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    mock_soil = MagicMock(ph=6.5, drainage="Moderately drained", approximate=False)
    with patch("apps.parcels.views.get_soil_data", return_value=mock_soil):
        client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    parcel.refresh_from_db()
    assert parcel.soil_source == "measured"


@pytest.mark.django_db
def test_soil_analyze_falls_back_to_macrostrat_when_soilgrids_fails(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    mock_soil = MagicMock(ph=7.5, drainage="Well-drained", approximate=True)
    with patch("apps.parcels.views.get_soil_data", side_effect=SoilGridsError("no data")), \
         patch("apps.parcels.views.get_geology_soil_data", return_value=mock_soil):
        client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    parcel.refresh_from_db()
    assert parcel.soil_ph == 7.5


@pytest.mark.django_db
def test_soil_analyze_sets_source_inferred_on_macrostrat_success(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    mock_soil = MagicMock(ph=7.5, drainage="Well-drained", approximate=True)
    with patch("apps.parcels.views.get_soil_data", side_effect=SoilGridsError("no data")), \
         patch("apps.parcels.views.get_geology_soil_data", return_value=mock_soil):
        client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    parcel.refresh_from_db()
    assert parcel.soil_source == "inferred"


@pytest.mark.django_db
def test_soil_analyze_returns_error_partial_when_both_sources_fail(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", polygon=SAMPLE_POLYGON, area_m2=100.0,
        latitude=48.85, longitude=2.35,
    )
    client = Client()
    client.force_login(user)
    with patch("apps.parcels.views.get_soil_data", side_effect=SoilGridsError("no data")), \
         patch("apps.parcels.views.get_geology_soil_data", side_effect=MacrostratError("API down")):
        response = client.post(f"/parcels/{parcel.pk}/soil-analyze/")
    assert b"We couldn&#x27;t reach our soil data source" in response.content
