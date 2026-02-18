import pytest
from apps.trees.models import TreeSpecies


@pytest.mark.django_db
def test_tree_species_str_format():
    species = TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb", "Cfa"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=20.0,
        maintenance_level="medium",
    )
    assert str(species) == "Wild Cherry (Prunus avium)"


@pytest.mark.django_db
def test_tree_species_filter_by_koppen_zone():
    TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb", "Cfa"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=20.0,
        maintenance_level="medium",
    )
    TreeSpecies.objects.create(
        scientific_name="Olea europaea",
        common_name="Olive",
        koppen_zones=["Csa", "Csb"],
        soil_ph_min=6.0,
        soil_ph_max=8.5,
        primary_use="fruit",
        max_height_m=12.0,
        maintenance_level="low",
    )
    compatible = TreeSpecies.objects.filter(koppen_zones__contains=["Cfb"])
    assert list(compatible.values_list("scientific_name", flat=True)) == ["Prunus avium"]
