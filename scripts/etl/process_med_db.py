"""Parse Mediterranean DB files and extract species attributes for Csa/Csb species."""

from __future__ import annotations

import csv
from pathlib import Path


def process_med_db(csv_path: Path) -> list[dict[str, object]]:
    """Extract species attributes (habitat, use) from Mediterranean DB CSV.

    Returns list of dicts with scientific_name and enrichment attributes.
    """
    results: list[dict[str, object]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            species_name = row.get("species", "").strip()
            if not species_name:
                continue
            entry: dict[str, object] = {"scientific_name": species_name}
            habitat = row.get("habitat", "").strip()
            if habitat:
                entry["habitat"] = habitat
            use = row.get("use", "").strip()
            if use:
                entry["primary_use"] = use
            results.append(entry)

    print(f"Extracted {len(results)} species from Mediterranean DB.")
    return results


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
    med_files = list(data_dir.glob("med_db*"))
    if med_files:
        for med_file in med_files:
            if med_file.suffix in (".csv", ".tsv"):
                result = process_med_db(med_file)
                print(f"Processed {len(result)} from {med_file.name}")
    else:
        print("No Mediterranean DB files found in data/raw/")
