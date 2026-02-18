import pytest

from scripts.etl.process_med_db import process_med_db


@pytest.fixture
def med_db_result(tmp_path):
    csv_content = "species,habitat,use\nOlea europaea,Mediterranean maquis,fruit\nQuercus ilex,Mediterranean forest,shade\n"
    csv_path = tmp_path / "med_species.csv"
    csv_path.write_text(csv_content, encoding="utf-8")
    return process_med_db(csv_path)


def test_process_med_db_extracts_correct_species_count(med_db_result):
    assert len(med_db_result) == 2


def test_process_med_db_maps_use_to_species(med_db_result):
    olea = next(r for r in med_db_result if r["scientific_name"] == "Olea europaea")
    assert olea["primary_use"] == "fruit"
