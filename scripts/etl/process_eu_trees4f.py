"""Parse EU-Trees4F data and extract current distribution data for 67 species."""

from __future__ import annotations

import csv
from pathlib import Path


def process_eu_trees4f(csv_path: Path) -> list[dict[str, object]]:
    """Extract species distribution data from EU-Trees4F CSV.

    Returns list of dicts with scientific_name and distribution info.
    """
    results: list[dict[str, object]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            species_name = row.get("species", "").strip()
            if not species_name:
                continue
            entry: dict[str, object] = {"scientific_name": species_name}
            distribution = row.get("distribution", "").strip()
            if distribution:
                entry["distribution"] = distribution
            results.append(entry)

    print(f"Extracted {len(results)} species from EU-Trees4F.")
    return results


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
    trees4f_files = list(data_dir.glob("eu_trees4f*"))
    if trees4f_files:
        for trees_file in trees4f_files:
            if trees_file.suffix in (".csv", ".tsv"):
                result = process_eu_trees4f(trees_file)
                print(f"Processed {len(result)} from {trees_file.name}")
    else:
        print("No EU-Trees4F files found in data/raw/")
