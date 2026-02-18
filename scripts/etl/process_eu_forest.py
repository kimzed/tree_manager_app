"""Parse EU-Forest CSV, convert coordinates, and derive Köppen zones per species."""

from __future__ import annotations

import csv
from pathlib import Path

import rasterio
import rasterio.transform
import rasterio.warp
import rasterio.windows

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
GEOTIFF_PATH = DATA_DIR / "koppen" / "koppen_geiger_0p00833333.tif"

# Pixel value → Köppen code (extracted from apps/parcels/services/koppen.py)
KOPPEN_CODES: dict[int, str] = {
    1: "Af", 2: "Am", 3: "Aw", 4: "BWh", 5: "BWk", 6: "BSh", 7: "BSk",
    8: "Csa", 9: "Csb", 10: "Csc", 11: "Cwa", 12: "Cwb", 13: "Cwc",
    14: "Cfa", 15: "Cfb", 16: "Cfc", 17: "Dsa", 18: "Dsb", 19: "Dsc",
    20: "Dsd", 21: "Dwa", 22: "Dwb", 23: "Dwc", 24: "Dwd", 25: "Dfa",
    26: "Dfb", 27: "Dfc", 28: "Dfd", 29: "ET", 30: "EF",
}


def convert_etrs89_to_wgs84(
    x_coords: list[float], y_coords: list[float],
) -> tuple[list[float], list[float]]:
    """Convert ETRS89-LAEA (EPSG:3035) coordinates to WGS84 (EPSG:4326) lon/lat."""
    lons, lats = rasterio.warp.transform(
        src_crs="EPSG:3035",
        dst_crs="EPSG:4326",
        xs=x_coords,
        ys=y_coords,
    )
    return lons, lats


def batch_koppen_lookup(
    lons: list[float], lats: list[float],
) -> list[str | None]:
    """Look up Köppen zone codes for a batch of WGS84 coordinates."""
    results: list[str | None] = []
    with rasterio.open(GEOTIFF_PATH) as src:
        band = src.read(1)
        for lon, lat in zip(lons, lats):
            try:
                row, col = src.index(lon, lat)
                if 0 <= row < band.shape[0] and 0 <= col < band.shape[1]:
                    pixel = int(band[row, col])
                    results.append(KOPPEN_CODES.get(pixel))
                else:
                    results.append(None)
            except (IndexError, ValueError):
                results.append(None)
    return results


def process_eu_forest(csv_path: Path) -> list[dict[str, object]]:
    """Parse EU-Forest CSV and derive Köppen zone compatibility per species.

    Returns list of dicts with scientific_name and koppen_zones.
    """
    # Collect unique coordinates per species
    species_coords: dict[str, set[tuple[float, float]]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            species_name = row.get("SPECIES NAME", "").strip()
            if not species_name:
                continue
            x_str = row.get("X", "")
            y_str = row.get("Y", "")
            if not x_str or not y_str:
                continue
            x_val = float(x_str)
            y_val = float(y_str)
            if species_name not in species_coords:
                species_coords[species_name] = set()
            species_coords[species_name].add((x_val, y_val))

    # Deduplicate all coordinates globally for batch conversion
    all_coords = set()
    for coords in species_coords.values():
        all_coords.update(coords)

    coord_list = list(all_coords)
    if not coord_list:
        return []

    x_coords = [c[0] for c in coord_list]
    y_coords = [c[1] for c in coord_list]

    print(f"Converting {len(coord_list):,} unique coordinates to WGS84...")
    lons, lats = convert_etrs89_to_wgs84(x_coords, y_coords)

    print("Looking up Köppen zones from GeoTIFF...")
    zones = batch_koppen_lookup(lons, lats)

    # Map coordinates to zones
    coord_to_zone: dict[tuple[float, float], str | None] = {}
    for coord, zone in zip(coord_list, zones):
        coord_to_zone[coord] = zone

    # Aggregate zones per species
    results: list[dict[str, object]] = []
    for species_name in sorted(species_coords.keys()):
        species_zones: set[str] = set()
        for coord in species_coords[species_name]:
            zone = coord_to_zone.get(coord)
            if zone is not None:
                species_zones.add(zone)
        if species_zones:
            results.append({
                "scientific_name": species_name,
                "koppen_zones": sorted(species_zones),
            })

    print(f"Extracted {len(results)} species with Köppen zone data.")
    return results


if __name__ == "__main__":
    import zipfile

    raw_dir = DATA_DIR / "raw"
    zip_path = raw_dir / "eu_forest.zip"
    csv_file = raw_dir / "EUForestspecies.csv"

    if not csv_file.exists() and zip_path.exists():
        print("Extracting EU-Forest zip...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(raw_dir)

    if csv_file.exists():
        result = process_eu_forest(csv_file)
        print(f"Processed {len(result)} species")
    else:
        print(f"EU-Forest CSV not found at {csv_file}")
