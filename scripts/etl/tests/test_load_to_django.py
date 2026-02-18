import json

import pytest
from apps.trees.models import TreeSpecies

SAMPLE_SPECIES = [
    {
        "scientific_name": "Prunus avium",
        "common_name": "Wild Cherry",
        "koppen_zones": ["Cfb", "Cfa"],
        "soil_ph_min": 5.5,
        "soil_ph_max": 7.5,
        "drought_tolerant": False,
        "primary_use": "fruit",
        "max_height_m": 20.0,
        "maintenance_level": "medium",
        "image_url": "",
        "attributes": ["Self-fertile", "Spring blossom"],
    },
]


@pytest.fixture
def species_json(tmp_path):
    json_path = tmp_path / "tree_species.json"
    json_path.write_text(json.dumps(SAMPLE_SPECIES), encoding="utf-8")
    return json_path


@pytest.mark.django_db
def test_load_creates_correct_count(species_json):
    from scripts.etl.load_to_django import load_species_from_json

    created, _updated = load_species_from_json(species_json)
    assert created == 1


@pytest.mark.django_db
def test_load_stores_species_data_correctly(species_json):
    from scripts.etl.load_to_django import load_species_from_json

    load_species_from_json(species_json)
    species = TreeSpecies.objects.get(scientific_name="Prunus avium")
    assert species.common_name == "Wild Cherry"
