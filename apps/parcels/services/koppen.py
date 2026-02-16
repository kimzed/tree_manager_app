from __future__ import annotations

import rasterio
import rasterio.errors
import rasterio.windows
from django.conf import settings


class KoppenError(Exception):
    """Raised when Köppen climate zone lookup fails."""


KOPPEN_ZONES: dict[int, str] = {
    1: "Af - Tropical rainforest",
    2: "Am - Tropical monsoon",
    3: "Aw - Tropical savanna",
    4: "BWh - Hot desert",
    5: "BWk - Cold desert",
    6: "BSh - Hot semi-arid",
    7: "BSk - Cold semi-arid",
    8: "Csa - Hot-summer Mediterranean",
    9: "Csb - Warm-summer Mediterranean",
    10: "Csc - Cold-summer Mediterranean",
    11: "Cwa - Monsoon-influenced humid subtropical",
    12: "Cwb - Subtropical highland",
    13: "Cwc - Cold subtropical highland",
    14: "Cfa - Humid subtropical",
    15: "Cfb - Oceanic",
    16: "Cfc - Subpolar oceanic",
    17: "Dsa - Hot-summer humid continental (Mediterranean)",
    18: "Dsb - Warm-summer humid continental (Mediterranean)",
    19: "Dsc - Subarctic (Mediterranean)",
    20: "Dsd - Extremely cold subarctic (Mediterranean)",
    21: "Dwa - Monsoon-influenced hot-summer humid continental",
    22: "Dwb - Monsoon-influenced warm-summer humid continental",
    23: "Dwc - Monsoon-influenced subarctic",
    24: "Dwd - Monsoon-influenced extremely cold subarctic",
    25: "Dfa - Hot-summer humid continental",
    26: "Dfb - Warm-summer humid continental",
    27: "Dfc - Subarctic",
    28: "Dfd - Extremely cold subarctic",
    29: "ET - Tundra",
    30: "EF - Ice cap",
}

_raster: rasterio.DatasetReader | None = None


def get_koppen_zone(lat: float, lon: float) -> str:
    """Look up Köppen climate zone from GeoTIFF for given coordinates."""
    global _raster  # noqa: PLW0603
    if _raster is None:
        geotiff_path = settings.KOPPEN_GEOTIFF_PATH
        if not geotiff_path.exists():
            raise KoppenError(
                "Köppen GeoTIFF not found. Run scripts/download_koppen.py first."
            )
        try:
            _raster = rasterio.open(geotiff_path)
        except rasterio.errors.RasterioIOError as exc:
            raise KoppenError(f"Failed to open Köppen GeoTIFF: {exc}") from exc

    row, col = _raster.index(lon, lat)
    pixel_value = int(
        _raster.read(1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0]
    )

    if pixel_value == 0 or pixel_value not in KOPPEN_ZONES:
        raise KoppenError(f"No climate data available for coordinates ({lat}, {lon})")

    return KOPPEN_ZONES[pixel_value]
