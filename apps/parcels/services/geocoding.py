from __future__ import annotations

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "TreeManagerApp/1.0"
TIMEOUT_SECONDS = 10


class GeocodingError(Exception):
    """Raised when the Nominatim API call fails."""


def geocode_address(address: str) -> dict[str, float | str] | None:
    """Geocode an address using Nominatim. Returns lat/lon/display_name or None."""
    try:
        response = httpx.get(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise GeocodingError(str(exc)) from exc
    results = response.json()
    if not results:
        return None
    hit = results[0]
    return {
        "lat": float(hit["lat"]),
        "lon": float(hit["lon"]),
        "display_name": hit["display_name"],
    }
