"""Load tree_species.json into Django TreeSpecies model."""

from __future__ import annotations

import json
import os
from pathlib import Path

PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"


def load_species_from_json(json_path: Path) -> tuple[int, int]:
    """Load species from JSON file into TreeSpecies model.

    Returns (created_count, updated_count).
    """
    from apps.trees.models import TreeSpecies

    with open(json_path, encoding="utf-8") as f:
        species_data = json.load(f)

    created_count = 0
    updated_count = 0

    for entry in species_data:
        _obj, created = TreeSpecies.objects.update_or_create(
            scientific_name=entry["scientific_name"],
            defaults={
                "common_name": entry.get("common_name", ""),
                "koppen_zones": entry.get("koppen_zones", []),
                "soil_ph_min": entry.get("soil_ph_min", 5.0),
                "soil_ph_max": entry.get("soil_ph_max", 7.5),
                "drought_tolerant": entry.get("drought_tolerant", False),
                "primary_use": entry.get("primary_use", "ornamental"),
                "max_height_m": entry.get("max_height_m", 15.0),
                "maintenance_level": entry.get("maintenance_level", "medium"),
                "image_url": entry.get("image_url", ""),
                "attributes": entry.get("attributes", []),
            },
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    total = created_count + updated_count
    print(f"Created: {created_count}, Updated: {updated_count}, Total: {total}")
    return created_count, updated_count


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    import django
    django.setup()

    json_path = PROCESSED_DIR / "tree_species.json"
    if json_path.exists():
        load_species_from_json(json_path)
    else:
        print(f"No species data found at {json_path}. Run build_tree_database.py first.")
