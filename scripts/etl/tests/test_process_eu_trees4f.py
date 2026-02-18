import pytest

from scripts.etl.process_eu_trees4f import process_eu_trees4f


@pytest.fixture
def eu_trees4f_result(tmp_path):
    csv_content = "species,distribution\nFagus sylvatica,Central and Western Europe\nPinus sylvestris,Northern Europe\n"
    csv_path = tmp_path / "trees4f_species.csv"
    csv_path.write_text(csv_content, encoding="utf-8")
    return process_eu_trees4f(csv_path)


def test_process_eu_trees4f_extracts_correct_species_count(eu_trees4f_result):
    assert len(eu_trees4f_result) == 2


def test_process_eu_trees4f_maps_distribution_to_species(eu_trees4f_result):
    fagus = next(r for r in eu_trees4f_result if r["scientific_name"] == "Fagus sylvatica")
    assert fagus["distribution"] == "Central and Western Europe"
