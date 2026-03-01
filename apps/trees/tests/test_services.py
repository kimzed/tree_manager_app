import pytest
from apps.parcels.models import Parcel
from apps.trees.services import get_compatible_mood_sets, get_trees_for_mood_set


@pytest.fixture
def user_for_parcel(db):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def cfb_parcel_with_user(db, mood_set_species, user_for_parcel):
    return Parcel.objects.create(
        user=user_for_parcel,
        name="Cfb parcel",
        climate_zone="Cfb - Oceanic",
        soil_ph=6.5,
    )


@pytest.fixture
def rare_climate_parcel(db, mood_set_species, user_for_parcel):
    return Parcel.objects.create(
        user=user_for_parcel,
        name="Rare parcel",
        climate_zone="ET - Tundra",
        soil_ph=6.5,
    )


@pytest.fixture
def partial_parcel(db, mood_set_species, user_for_parcel):
    return Parcel.objects.create(
        user=user_for_parcel,
        name="Partial parcel",
        climate_zone="Cfb - Oceanic",
        soil_ph=None,
    )


def test_get_compatible_mood_sets_filters_by_climate(cfb_parcel_with_user):
    results = get_compatible_mood_sets(cfb_parcel_with_user)

    assert all(count > 0 for _, count in results)


def test_mood_set_zero_compatible_trees(rare_climate_parcel):
    results = get_compatible_mood_sets(rare_climate_parcel)

    assert all(count == 0 for _, count in results)


def test_get_compatible_mood_sets_partial_profile(partial_parcel):
    results = get_compatible_mood_sets(partial_parcel)

    assert all(count > 0 for _, count in results)


def test_get_trees_for_mood_set_returns_compatible_trees(cfb_parcel_with_user):
    trees = get_trees_for_mood_set(cfb_parcel_with_user, "low-effort-abundance")

    assert len(trees) == 10


def test_get_trees_for_mood_set_invalid_key_returns_empty(cfb_parcel_with_user):
    trees = get_trees_for_mood_set(cfb_parcel_with_user, "nonexistent-mood")

    assert trees == []
