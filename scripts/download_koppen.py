"""Download the Beck et al. (2018) Köppen-Geiger GeoTIFF to data/koppen/."""
from __future__ import annotations

from pathlib import Path

import httpx

DOWNLOAD_URL = (
    "https://figshare.com/ndownloader/files/12407516"
)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "koppen"
OUTPUT_FILE = OUTPUT_DIR / "Beck_KG_V1_present_0p0083.tif"


def download() -> None:
    if OUTPUT_FILE.exists():
        print(f"File already exists: {OUTPUT_FILE}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Köppen GeoTIFF to {OUTPUT_FILE}...")

    with httpx.stream("GET", DOWNLOAD_URL, follow_redirects=True, timeout=300) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(OUTPUT_FILE, "wb") as file:
            for chunk in response.iter_bytes(chunk_size=8192):
                file.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    print(f"\r  {pct}% ({downloaded // 1024 // 1024}MB / {total // 1024 // 1024}MB)", end="", flush=True)

    print(f"\nDone: {OUTPUT_FILE}")


if __name__ == "__main__":
    download()
