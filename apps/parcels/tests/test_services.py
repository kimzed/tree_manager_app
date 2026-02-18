from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import numpy as np
import pytest

from apps.parcels.services.koppen import KoppenError, get_koppen_zone
from apps.parcels.services.macrostrat import MacrostratError, get_geology_soil_data
from apps.parcels.services.soilgrids import SoilGridsError, get_soil_data
import apps.parcels.services.koppen as koppen_module


@pytest.fixture(autouse=True)
def reset_singleton():
    koppen_module._raster = None
    yield
    koppen_module._raster = None


@pytest.fixture
def mock_raster():
    raster = MagicMock()
    raster.index.return_value = (1000, 2000)
    raster.read.return_value = np.array([[15]])
    return raster


def test_get_koppen_zone_returns_formatted_zone_string(mock_raster):
    with patch("apps.parcels.services.koppen.rasterio") as mock_rasterio:
        mock_rasterio.open.return_value = mock_raster
        mock_rasterio.windows.Window = MagicMock()
        with patch("apps.parcels.services.koppen.settings") as mock_settings:
            mock_settings.KOPPEN_GEOTIFF_PATH = MagicMock()
            mock_settings.KOPPEN_GEOTIFF_PATH.exists.return_value = True
            result = get_koppen_zone(48.85, 2.35)
    assert result == "Cfb - Oceanic"


def test_get_koppen_zone_raises_error_when_geotiff_not_found():
    with patch("apps.parcels.services.koppen.settings") as mock_settings:
        mock_settings.KOPPEN_GEOTIFF_PATH = Path("/nonexistent/path.tif")
        with pytest.raises(KoppenError, match="Köppen GeoTIFF not found"):
            get_koppen_zone(48.85, 2.35)


def test_get_koppen_zone_raises_error_for_nodata_value(mock_raster):
    mock_raster.read.return_value = np.array([[0]])
    with patch("apps.parcels.services.koppen.rasterio") as mock_rasterio:
        mock_rasterio.open.return_value = mock_raster
        mock_rasterio.windows.Window = MagicMock()
        with patch("apps.parcels.services.koppen.settings") as mock_settings:
            mock_settings.KOPPEN_GEOTIFF_PATH = MagicMock()
            mock_settings.KOPPEN_GEOTIFF_PATH.exists.return_value = True
            with pytest.raises(KoppenError, match="No climate data available"):
                get_koppen_zone(48.85, 2.35)


# --- Story 2.5: SoilGrids service tests ---


MOCK_SOILGRIDS_RESPONSE = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [2.35, 48.85]},
    "properties": {
        "layers": [
            {
                "name": "phh2o",
                "depths": [{"label": "0-30cm", "values": {"mean": 65}}],
            },
            {
                "name": "clay",
                "depths": [{"label": "0-30cm", "values": {"mean": 250}}],
            },
            {
                "name": "sand",
                "depths": [{"label": "0-30cm", "values": {"mean": 350}}],
            },
        ]
    },
}


def _mock_response(json_data, status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_get_soil_data_returns_correct_ph():
    with patch("apps.parcels.services.soilgrids.httpx.get", return_value=_mock_response(MOCK_SOILGRIDS_RESPONSE)):
        result = get_soil_data(48.85, 2.35)
    assert result.ph == 6.5


def test_get_soil_data_derives_moderately_drained_when_neither_dominant():
    with patch("apps.parcels.services.soilgrids.httpx.get", return_value=_mock_response(MOCK_SOILGRIDS_RESPONSE)):
        result = get_soil_data(48.85, 2.35)
    assert result.drainage == "Moderately drained"


def test_get_soil_data_derives_well_drained_when_sand_high():
    response = {
        "properties": {
            "layers": [
                {"name": "phh2o", "depths": [{"values": {"mean": 60}}]},
                {"name": "clay", "depths": [{"values": {"mean": 100}}]},
                {"name": "sand", "depths": [{"values": {"mean": 700}}]},
            ]
        }
    }
    with patch("apps.parcels.services.soilgrids.httpx.get", return_value=_mock_response(response)):
        result = get_soil_data(48.85, 2.35)
    assert result.drainage == "Well-drained"


def test_get_soil_data_derives_poorly_drained_when_clay_high():
    response = {
        "properties": {
            "layers": [
                {"name": "phh2o", "depths": [{"values": {"mean": 60}}]},
                {"name": "clay", "depths": [{"values": {"mean": 450}}]},
                {"name": "sand", "depths": [{"values": {"mean": 200}}]},
            ]
        }
    }
    with patch("apps.parcels.services.soilgrids.httpx.get", return_value=_mock_response(response)):
        result = get_soil_data(48.85, 2.35)
    assert result.drainage == "Poorly drained"


def test_get_soil_data_raises_error_on_timeout():
    with patch("apps.parcels.services.soilgrids.httpx.get", side_effect=httpx.TimeoutException("timed out")):
        with pytest.raises(SoilGridsError, match="timed out"):
            get_soil_data(48.85, 2.35)


def test_get_soil_data_raises_error_on_http_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_resp,
    )
    with patch("apps.parcels.services.soilgrids.httpx.get", return_value=mock_resp):
        with pytest.raises(SoilGridsError, match="500"):
            get_soil_data(48.85, 2.35)


MOCK_NONE_RESPONSE = {
    "properties": {
        "layers": [
            {"name": "phh2o", "depths": [{"values": {"mean": None}}]},
            {"name": "clay", "depths": [{"values": {"mean": None}}]},
            {"name": "sand", "depths": [{"values": {"mean": None}}]},
        ]
    },
}


def test_get_soil_data_falls_back_to_nearby_when_original_has_no_data():
    with patch("apps.parcels.services.soilgrids.httpx.get", side_effect=[
        _mock_response(MOCK_NONE_RESPONSE),
        _mock_response(MOCK_SOILGRIDS_RESPONSE),
    ]):
        result = get_soil_data(48.85, 2.35)
    assert result.approximate is True


def test_get_soil_data_is_not_approximate_when_original_has_data():
    with patch("apps.parcels.services.soilgrids.httpx.get", return_value=_mock_response(MOCK_SOILGRIDS_RESPONSE)):
        result = get_soil_data(48.85, 2.35)
    assert result.approximate is False


def test_get_soil_data_raises_error_when_no_nearby_data():
    with patch("apps.parcels.services.soilgrids.httpx.get", return_value=_mock_response(MOCK_NONE_RESPONSE)):
        with pytest.raises(SoilGridsError, match="no data"):
            get_soil_data(48.85, 2.35)


# --- Story 2.5b: Macrostrat service tests ---


MOCK_MACROSTRAT_RESPONSE = {
    "success": {"v": 2},
    "data": [
        {
            "map_id": 12345,
            "name": "Paris Basin",
            "lith": "limestone [60.0%..80.0%]; clay [20.0%..40.0%]",
            "liths": [1, 2],
            "best_int_name": "Cretaceous",
        }
    ],
}


def test_get_geology_soil_data_returns_correct_ph_for_limestone():
    with patch("apps.parcels.services.macrostrat.httpx.get", return_value=_mock_response(MOCK_MACROSTRAT_RESPONSE)):
        result = get_geology_soil_data(48.85, 2.35)
    assert result.ph == 7.5


def test_get_geology_soil_data_returns_correct_drainage_for_limestone():
    with patch("apps.parcels.services.macrostrat.httpx.get", return_value=_mock_response(MOCK_MACROSTRAT_RESPONSE)):
        result = get_geology_soil_data(48.85, 2.35)
    assert result.drainage == "Well-drained"


def test_get_geology_soil_data_raises_error_on_timeout():
    with patch("apps.parcels.services.macrostrat.httpx.get", side_effect=httpx.TimeoutException("timed out")):
        with pytest.raises(MacrostratError, match="timed out"):
            get_geology_soil_data(48.85, 2.35)


def test_get_geology_soil_data_raises_error_on_empty_data():
    empty_response = {"success": {"v": 2}, "data": []}
    with patch("apps.parcels.services.macrostrat.httpx.get", return_value=_mock_response(empty_response)):
        with pytest.raises(MacrostratError, match="No geology data"):
            get_geology_soil_data(48.85, 2.35)


def test_get_geology_soil_data_raises_error_on_http_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_resp,
    )
    with patch("apps.parcels.services.macrostrat.httpx.get", return_value=mock_resp):
        with pytest.raises(MacrostratError, match="500"):
            get_geology_soil_data(48.85, 2.35)


def test_get_geology_soil_data_raises_error_on_empty_lith():
    response_data = {
        "success": {"v": 2},
        "data": [{"map_id": 1, "name": "Unit", "lith": "", "liths": []}],
    }
    with patch("apps.parcels.services.macrostrat.httpx.get", return_value=_mock_response(response_data)):
        with pytest.raises(MacrostratError, match="No lithology data"):
            get_geology_soil_data(48.85, 2.35)


def test_get_geology_soil_data_returns_approximate_true():
    with patch("apps.parcels.services.macrostrat.httpx.get", return_value=_mock_response(MOCK_MACROSTRAT_RESPONSE)):
        result = get_geology_soil_data(48.85, 2.35)
    assert result.approximate is True
