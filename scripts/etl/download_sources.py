"""Download EU-Forest, Mediterranean DB, and EU-Trees4F source files to data/raw/."""

from __future__ import annotations

from pathlib import Path

import httpx

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"

SOURCES: list[dict[str, str]] = [
    {
        "name": "EU-Forest",
        "url": "https://ndownloader.figshare.com/articles/6497104/versions/1",
        "filename": "eu_forest.zip",
    },
    {
        "name": "Mediterranean DB",
        "url": "https://entrepot.recherche.data.gouv.fr/api/access/dataset/:persistentId?persistentId=doi:10.57745/GDKAJV",
        "filename": "med_db.zip",
    },
    {
        "name": "EU-Trees4F",
        "url": "https://ndownloader.figshare.com/collections/5525688/versions/4",
        "filename": "eu_trees4f.zip",
    },
]


def download_file(url: str, dest: Path, name: str) -> None:
    """Download a file from url to dest with progress output."""
    print(f"Downloading {name} from {url}...")
    with httpx.stream("GET", url, follow_redirects=True, timeout=300.0) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = downloaded * 100 // total
                    print(f"\r  {downloaded:,} / {total:,} bytes ({pct}%)", end="", flush=True)
        print(f"\n  Saved to {dest}")


def download_all() -> None:
    """Download all source files to data/raw/."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for source in SOURCES:
        dest = RAW_DIR / source["filename"]
        if dest.exists():
            print(f"Skipping {source['name']} — already downloaded at {dest}")
            continue
        download_file(source["url"], dest, source["name"])
    print("All downloads complete.")


if __name__ == "__main__":
    download_all()
