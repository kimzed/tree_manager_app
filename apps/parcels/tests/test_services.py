from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from apps.parcels.services.koppen import KoppenError, get_koppen_zone
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
