import pytest

from scripts.etl.build_tree_database import merge_layers


@pytest.fixture
def merged_result():
    eu_forest_data = [
        {"scientific_name": "Prunus avium", "koppen_zones": ["Cfb", "Cfa"]},
        {"scientific_name": "Olea europaea", "koppen_zones": ["Csa", "Csb"]},
    ]
    med_db_data = [
        {"scientific_name": "Olea europaea", "primary_use": "fruit", "habitat": "Mediterranean"},
    ]
    eu_trees4f_data = [
        {"scientific_name": "Prunus avium", "distribution": "Central Europe"},
    ]
    return merge_layers(eu_forest_data, med_db_data, eu_trees4f_data)


def test_merge_preserves_eu_forest_koppen_zones(merged_result):
    prunus = next(r for r in merged_result if r["scientific_name"] == "Prunus avium")
    assert prunus["koppen_zones"] == ["Cfb", "Cfa"]


def test_merge_applies_species_defaults_common_name(merged_result):
    prunus = next(r for r in merged_result if r["scientific_name"] == "Prunus avium")
    assert prunus["common_name"] == "Wild Cherry"


def test_merge_includes_eu_forest_species_without_defaults():
    eu_forest_data = [
        {"scientific_name": "Unknown species xyz", "koppen_zones": ["Cfb"]},
    ]
    result = merge_layers(eu_forest_data, [], [])
    species_names = [str(r["scientific_name"]) for r in result]
    assert "Unknown species xyz" in species_names
