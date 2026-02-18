from unittest.mock import patch

import pytest

from scripts.etl.process_eu_forest import process_eu_forest

SAMPLE_CSV = (
    "X\tY\tCOUNTRY\tSPECIES NAME\tDBH\n"
    "4321000\t2881000\tFR\tQuercus robur\t20\n"
    "4321000\t2881000\tFR\tQuercus robur\t30\n"
    "4500000\t2700000\tIT\tOlea europaea\t15\n"
)


@pytest.fixture
def eu_forest_result(tmp_path):
    csv_path = tmp_path / "test_eu_forest.csv"
    csv_path.write_text(SAMPLE_CSV, encoding="utf-8")
    with patch("scripts.etl.process_eu_forest.convert_etrs89_to_wgs84") as mock_convert, \
         patch("scripts.etl.process_eu_forest.batch_koppen_lookup") as mock_lookup:
        mock_convert.return_value = ([2.35, 10.0], [48.85, 42.0])
        mock_lookup.return_value = ["Cfb", "Csa"]
        return process_eu_forest(csv_path)


def test_process_eu_forest_extracts_correct_species_count(eu_forest_result):
    assert len(eu_forest_result) == 2


def test_process_eu_forest_maps_zones_to_species(eu_forest_result):
    olea = next(r for r in eu_forest_result if r["scientific_name"] == "Olea europaea")
    assert olea["koppen_zones"] == ["Csa"]
