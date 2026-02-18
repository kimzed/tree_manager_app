from __future__ import annotations

from typing import Any

import httpx

from apps.parcels.services.soilgrids import SoilData

MACROSTRAT_API_URL = "https://macrostrat.org/api/v2/geologic_units/map"

LITHOLOGY_SOIL_MAP: dict[str, tuple[float, str]] = {
    "limestone": (7.5, "Well-drained"),
    "chalk": (7.5, "Well-drained"),
    "dolomite": (7.5, "Well-drained"),
    "sandstone": (6.0, "Well-drained"),
    "sand": (6.0, "Well-drained"),
    "clay": (7.0, "Poorly drained"),
    "mudstone": (7.0, "Poorly drained"),
    "shale": (7.0, "Poorly drained"),
    "silt": (6.5, "Moderately drained"),
    "siltstone": (6.5, "Moderately drained"),
    "gravel": (6.5, "Well-drained"),
    "conglomerate": (6.5, "Well-drained"),
    "alluvium": (6.5, "Well-drained"),
    "granite": (5.5, "Well-drained"),
    "gneiss": (5.5, "Well-drained"),
    "schist": (5.5, "Well-drained"),
    "basalt": (6.5, "Moderately drained"),
    "volcanic": (6.5, "Moderately drained"),
    "marl": (7.0, "Moderately drained"),
}

DEFAULT_SOIL = (6.5, "Moderately drained")


class MacrostratError(Exception):
    """Raised when Macrostrat API call fails."""


def _parse_dominant_lithology(lith_string: str) -> str:
    first_entry = lith_string.split(";")[0].strip()
    name = first_entry.split("[")[0].strip().lower()
    return name


def get_geology_soil_data(lat: float, lon: float) -> SoilData:
    """Infer soil properties from underlying geology via Macrostrat API."""
    params: dict[str, Any] = {"lat": lat, "lng": lon, "response": "long"}
    try:
        response = httpx.get(MACROSTRAT_API_URL, params=params, timeout=10.0)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise MacrostratError("Macrostrat API timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise MacrostratError(f"Macrostrat API returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise MacrostratError(f"Macrostrat API request failed: {exc}") from exc

    data = response.json()
    records = data.get("data", [])
    if not records:
        raise MacrostratError("No geology data available for this location")

    lith_string = records[0].get("lith", "")
    if not lith_string:
        raise MacrostratError("No lithology data in Macrostrat response")

    dominant = _parse_dominant_lithology(lith_string)

    for keyword, (ph, drainage) in LITHOLOGY_SOIL_MAP.items():
        if keyword in dominant:
            return SoilData(ph=ph, drainage=drainage, approximate=True)

    ph, drainage = DEFAULT_SOIL
    return SoilData(ph=ph, drainage=drainage, approximate=True)
