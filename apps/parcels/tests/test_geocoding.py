import httpx
import pytest
from unittest.mock import patch, MagicMock
from apps.parcels.services.geocoding import geocode_address, GeocodingError


def test_geocode_address_returns_location():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"lat": "48.8566", "lon": "2.3522", "display_name": "Paris, France"}
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("apps.parcels.services.geocoding.httpx.get", return_value=mock_response):
        result = geocode_address("Paris")

    assert result == {"lat": 48.8566, "lon": 2.3522, "display_name": "Paris, France"}


def test_geocode_address_returns_none_for_empty_results():
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch("apps.parcels.services.geocoding.httpx.get", return_value=mock_response):
        result = geocode_address("nonexistent place xyz")

    assert result is None


def test_geocode_address_raises_geocoding_error_on_http_failure():
    with patch(
        "apps.parcels.services.geocoding.httpx.get",
        side_effect=httpx.TimeoutException("timed out"),
    ):
        with pytest.raises(GeocodingError):
            geocode_address("Paris")
