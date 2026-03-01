from unittest.mock import patch

import pytest
from django.test import Client as DjangoClient

from apps.parcels.models import Parcel
from apps.recommendations.services.recommender import TreeRecommendation
from apps.trees.models import TreeSpecies


@pytest.mark.django_db
def test_profile_template_shows_find_my_trees_button(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", area_m2=100.0,
        latitude=48.85, longitude=2.35, climate_zone="Cfb - Oceanic",
        soil_ph=6.5, soil_drainage="Well-drained",
    )
    client = DjangoClient()
    client.force_login(user)
    response = client.get(f"/parcels/{parcel.pk}/")
    assert b"Find My Trees" in response.content


@pytest.mark.django_db
def test_results_partial_renders_tree_cards_in_grid(user):
    tree = TreeSpecies.objects.create(
        scientific_name="Prunus avium", common_name="Wild Cherry",
        koppen_zones=["Cfb"], soil_ph_min=5.0, soil_ph_max=8.0,
        primary_use="fruit", max_height_m=15.0, maintenance_level="low",
        image_url="https://example.com/cherry.jpg",
        attributes=["Fruit", "Low care"],
    )
    parcel = Parcel.objects.create(
        user=user, name="Garden", area_m2=100.0,
        latitude=48.85, longitude=2.35, climate_zone="Cfb - Oceanic",
        soil_ph=6.5, soil_drainage="Well-drained",
    )
    client = DjangoClient()
    client.force_login(user)
    with patch(
        "apps.recommendations.views.generate_recommendations",
        return_value=[TreeRecommendation(scientific_name="Prunus avium", rank=1, explanation="Thrives in your climate", tree=tree)],
    ):
        response = client.post(f"/recommendations/{parcel.pk}/generate/")
    assert b"Wild Cherry" in response.content


@pytest.mark.django_db
def test_view_includes_mood_sets_with_compatible_counts(user):
    TreeSpecies.objects.create(
        scientific_name="Prunus avium", common_name="Wild Cherry",
        koppen_zones=["Cfb"], soil_ph_min=5.0, soil_ph_max=8.0,
        primary_use="fruit", max_height_m=15.0, maintenance_level="low",
    )
    parcel = Parcel.objects.create(
        user=user, name="Garden", area_m2=100.0,
        latitude=48.85, longitude=2.35, climate_zone="Cfb - Oceanic",
        soil_ph=6.5, soil_drainage="Well-drained",
    )
    client = DjangoClient()
    client.force_login(user)
    with patch(
        "apps.recommendations.views.generate_recommendations",
        return_value=[TreeRecommendation(scientific_name="Prunus avium", rank=1, explanation="Great", tree=None)],
    ):
        response = client.post(f"/recommendations/{parcel.pk}/generate/")
    assert b"Low-Effort Abundance" in response.content


@pytest.mark.django_db
def test_empty_recommendations_shows_no_trees_message(user):
    parcel = Parcel.objects.create(
        user=user, name="Garden", area_m2=100.0,
        latitude=48.85, longitude=2.35, climate_zone="Cfb - Oceanic",
        soil_ph=6.5, soil_drainage="Well-drained",
    )
    client = DjangoClient()
    client.force_login(user)
    with patch(
        "apps.recommendations.views.generate_recommendations",
        return_value=[],
    ):
        response = client.post(f"/recommendations/{parcel.pk}/generate/")
    assert b"No matching trees found" in response.content


@pytest.mark.django_db
def test_error_partial_renders_retry_button(user):
    from apps.recommendations.services.llm import RecommendationError

    parcel = Parcel.objects.create(
        user=user, name="Garden", area_m2=100.0,
        latitude=48.85, longitude=2.35, climate_zone="Cfb - Oceanic",
        soil_ph=6.5, soil_drainage="Well-drained",
    )
    client = DjangoClient()
    client.force_login(user)
    with patch(
        "apps.recommendations.views.generate_recommendations",
        side_effect=RecommendationError("API down"),
    ):
        response = client.post(f"/recommendations/{parcel.pk}/generate/")
    assert b"Retry" in response.content
