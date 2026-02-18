import pytest
from apps.trees.filters import filter_trees
from apps.trees.models import TreeSpecies


@pytest.fixture
def fruit_cherry(db):
    return TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=20.0,
        maintenance_level="medium",
    )


@pytest.fixture
def ornamental_birch(db):
    return TreeSpecies.objects.create(
        scientific_name="Betula pendula",
        common_name="Silver Birch",
        koppen_zones=["Cfb", "Dfb"],
        soil_ph_min=4.5,
        soil_ph_max=7.0,
        primary_use="ornamental",
        max_height_m=12.0,
        maintenance_level="low",
    )


@pytest.fixture
def shade_oak(db):
    return TreeSpecies.objects.create(
        scientific_name="Quercus robur",
        common_name="English Oak",
        koppen_zones=["Cfb"],
        soil_ph_min=4.5,
        soil_ph_max=7.5,
        primary_use="shade",
        max_height_m=25.0,
        maintenance_level="low",
    )


@pytest.fixture
def small_crab_apple(db):
    return TreeSpecies.objects.create(
        scientific_name="Malus sylvestris",
        common_name="Crab Apple",
        koppen_zones=["Cfb"],
        soil_ph_min=5.0,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=6.0,
        maintenance_level="low",
    )


@pytest.mark.django_db
def test_filter_by_primary_use(fruit_cherry, ornamental_birch, shade_oak):
    result = filter_trees(TreeSpecies.objects.all(), primary_use="fruit")
    assert list(result) == [fruit_cherry]


@pytest.mark.django_db
def test_filter_by_size_small(fruit_cherry, small_crab_apple, shade_oak):
    result = filter_trees(TreeSpecies.objects.all(), size="small")
    assert list(result) == [small_crab_apple]


@pytest.mark.django_db
def test_filter_by_maintenance_level(fruit_cherry, ornamental_birch, shade_oak):
    result = filter_trees(TreeSpecies.objects.all(), maintenance_level="low")
    assert list(result) == [shade_oak, ornamental_birch]


@pytest.mark.django_db
def test_combined_filters(fruit_cherry, ornamental_birch, shade_oak, small_crab_apple):
    result = filter_trees(TreeSpecies.objects.all(), primary_use="fruit", size="small")
    assert list(result) == [small_crab_apple]
