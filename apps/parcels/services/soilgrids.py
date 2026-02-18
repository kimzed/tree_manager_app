from __future__ import annotations

from typing import Any, NamedTuple

import httpx

SOILGRIDS_API_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"

# Nearby offsets in cardinal directions at ~5km, ~15km, ~25km (degrees)
_NEARBY_OFFSETS: list[tuple[float, float]] = [
    (0.05, 0.0), (-0.05, 0.0), (0.0, 0.05), (0.0, -0.05),
    (0.13, 0.0), (-0.13, 0.0), (0.0, 0.13), (0.0, -0.13),
    (0.22, 0.0), (-0.22, 0.0), (0.0, 0.22), (0.0, -0.22),
]


class SoilGridsError(Exception):
    """Raised when SoilGrids API call fails."""


class SoilData(NamedTuple):
    ph: float
    drainage: str
    approximate: bool = False


def _derive_drainage(clay_pct: float, sand_pct: float) -> str:
    if sand_pct >= 65:
        return "Well-drained"
    if clay_pct >= 40:
        return "Poorly drained"
    return "Moderately drained"


def _fetch_point(lat: float, lon: float) -> tuple[float, float, float] | None:
    """Fetch raw soil values for a single point. Returns (ph, clay, sand) or None."""
    params: dict[str, Any] = {
        "lon": lon,
        "lat": lat,
        "property": ["phh2o", "clay", "sand"],
        "depth": "0-5cm",
        "value": "mean",
    }
    try:
        response = httpx.get(SOILGRIDS_API_URL, params=params, timeout=10.0)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise SoilGridsError("SoilGrids API timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise SoilGridsError(f"SoilGrids API returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise SoilGridsError(f"SoilGrids API request failed: {exc}") from exc

    data = response.json()
    try:
        layers = {
            layer["name"]: layer["depths"][0]["values"]["mean"]
            for layer in data["properties"]["layers"]
        }
        raw_ph = layers["phh2o"]
        raw_clay = layers["clay"]
        raw_sand = layers["sand"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SoilGridsError("Unexpected SoilGrids response format") from exc

    if raw_ph is None or raw_clay is None or raw_sand is None:
        return None

    return (float(raw_ph), float(raw_clay), float(raw_sand))


def get_soil_data(lat: float, lon: float) -> SoilData:
    """Fetch soil pH and texture from SoilGrids API, derive drainage.

    Falls back to nearby points (~2km, ~5km) if original location has no data.
    """
    offsets = [(0.0, 0.0), *_NEARBY_OFFSETS]

    for dlat, dlon in offsets:
        raw = _fetch_point(lat + dlat, lon + dlon)
        if raw is not None:
            ph = raw[0] / 10
            clay_pct = raw[1] * 0.1
            sand_pct = raw[2] * 0.1
            approximate = dlat != 0.0 or dlon != 0.0
            return SoilData(
                ph=round(ph, 1),
                drainage=_derive_drainage(clay_pct, sand_pct),
                approximate=approximate,
            )

    raise SoilGridsError("SoilGrids returned no data for this location or nearby areas")
