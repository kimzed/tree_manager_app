"""Download the Beck et al. (2023) Köppen-Geiger GeoTIFF to data/koppen/.

Source: https://figshare.com/articles/dataset/High-resolution_1_km_K_ppen-Geiger_maps_for_1901_2099_based_on_constrained_CMIP6_projections/21789074
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import httpx

ARTICLE_ID = "21789074"
API_URL = f"https://api.figshare.com/v2/articles/{ARTICLE_ID}/files"
ZIP_NAME = "koppen_geiger_tif.zip"
GEOTIFF_IN_ZIP = "koppen_geiger_tif/1991_2020/koppen_geiger_0p00833333.tif"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "koppen"
OUTPUT_FILE = OUTPUT_DIR / "koppen_geiger_0p00833333.tif"

MANUAL_URL = (
    "https://figshare.com/articles/dataset/"
    "High-resolution_1_km_K_ppen-Geiger_maps_for_1901_2099_based_on_constrained_CMIP6_projections/21789074"
)


def _get_download_url() -> str:
    """Resolve the download URL for the GeoTIFF zip via figshare API."""
    response = httpx.get(API_URL, timeout=30)
    response.raise_for_status()
    for file_info in response.json():
        if file_info["name"] == ZIP_NAME:
            return file_info["download_url"]
    raise RuntimeError(f"Could not find {ZIP_NAME} in figshare article {ARTICLE_ID}")


def download() -> None:
    if OUTPUT_FILE.exists():
        print(f"File already exists: {OUTPUT_FILE}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OUTPUT_DIR / ZIP_NAME

    print(f"Resolving download URL from figshare API...")
    try:
        url = _get_download_url()
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"Failed to resolve download URL: {exc}")
        print(f"\nDownload manually from:\n  {MANUAL_URL}")
        print(f"Then extract '{GEOTIFF_IN_ZIP}' to:\n  {OUTPUT_FILE}")
        return

    print(f"Downloading {ZIP_NAME}...")
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=600) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            with open(zip_path, "wb") as file:
                for chunk in response.iter_bytes(chunk_size=8192):
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded * 100 // total
                        print(f"\r  {pct}% ({downloaded // 1024 // 1024}MB / {total // 1024 // 1024}MB)", end="", flush=True)
            print()
    except httpx.HTTPError as exc:
        zip_path.unlink(missing_ok=True)
        print(f"Download failed: {exc}")
        print(f"\nDownload manually from:\n  {MANUAL_URL}")
        print(f"Then extract '{GEOTIFF_IN_ZIP}' to:\n  {OUTPUT_FILE}")
        return

    print("Extracting GeoTIFF...")
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(GEOTIFF_IN_ZIP) as src, open(OUTPUT_FILE, "wb") as dst:
            dst.write(src.read())

    zip_path.unlink()
    print(f"Done: {OUTPUT_FILE}")


if __name__ == "__main__":
    download()
