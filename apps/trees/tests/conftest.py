import pytest
from apps.trees.constants import MOOD_SETS
from apps.trees.models import TreeSpecies


@pytest.fixture
def mood_set_species(db):
    all_names = {name for mood in MOOD_SETS for name in mood.scientific_names}
    for name in all_names:
        TreeSpecies.objects.create(
            scientific_name=name,
            common_name=f"Test {name.split()[-1].title()}",
            koppen_zones=["Cfb"],
            soil_ph_min=5.0,
            soil_ph_max=7.5,
            primary_use="ornamental",
            max_height_m=10.0,
            maintenance_level="low",
        )
