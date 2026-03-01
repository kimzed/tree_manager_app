from unittest.mock import patch

import pytest

from apps.parcels.models import Parcel
from apps.recommendations.services.llm import RecommendationError
from apps.recommendations.services.recommender import (
    TreeRecommendation,
    format_tree_list,
    generate_recommendations,
    get_compatible_trees,
    parse_recommendations,
)
from apps.trees.models import TreeSpecies


@pytest.mark.django_db
def test_get_compatible_trees_filters_by_climate_zone(user):
    matching = TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb", "Dfb"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=15.0,
        maintenance_level="low",
    )
    TreeSpecies.objects.create(
        scientific_name="Citrus sinensis",
        common_name="Orange",
        koppen_zones=["Csa", "Cfa"],
        soil_ph_min=5.5,
        soil_ph_max=7.0,
        primary_use="fruit",
        max_height_m=10.0,
        maintenance_level="medium",
    )
    parcel = Parcel.objects.create(
        user=user, name="Garden", climate_zone="Cfb - Oceanic",
        soil_ph=6.5, soil_drainage="Well-drained", area_m2=200.0,
        latitude=48.85, longitude=2.35,
    )
    result = list(get_compatible_trees(parcel))
    assert result == [matching]


@pytest.mark.django_db
def test_get_compatible_trees_filters_by_soil_ph(user):
    matching = TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=15.0,
        maintenance_level="low",
    )
    TreeSpecies.objects.create(
        scientific_name="Vaccinium corymbosum",
        common_name="Blueberry",
        koppen_zones=["Cfb"],
        soil_ph_min=4.0,
        soil_ph_max=5.5,
        primary_use="fruit",
        max_height_m=2.0,
        maintenance_level="medium",
    )
    parcel = Parcel.objects.create(
        user=user, name="Garden", climate_zone="Cfb - Oceanic",
        soil_ph=6.5, soil_drainage="Well-drained", area_m2=200.0,
        latitude=48.85, longitude=2.35,
    )
    result = list(get_compatible_trees(parcel))
    assert result == [matching]


@pytest.mark.django_db
def test_format_tree_list_produces_expected_string():
    tree = TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=15.0,
        maintenance_level="low",
        attributes=["Self-fertile", "Fast-growing"],
    )
    result = format_tree_list(TreeSpecies.objects.filter(pk=tree.pk))
    assert result == (
        "- Prunus avium (Wild Cherry): fruit, 15.0m max, low maintenance, "
        "Self-fertile, Fast-growing"
    )


@pytest.mark.django_db
def test_parse_recommendations_matches_trees():
    tree = TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=15.0,
        maintenance_level="low",
    )
    raw_json = '[{"scientific_name": "Prunus avium", "rank": 1, "explanation": "Thrives in Cfb climate"}]'
    result = parse_recommendations(raw_json, TreeSpecies.objects.all())
    assert result == [
        TreeRecommendation(
            scientific_name="Prunus avium",
            rank=1,
            explanation="Thrives in Cfb climate",
            tree=tree,
        )
    ]


@pytest.mark.django_db
def test_parse_recommendations_handles_unknown_species():
    raw_json = '[{"scientific_name": "Unknown species", "rank": 1, "explanation": "Good tree"}]'
    result = parse_recommendations(raw_json, TreeSpecies.objects.none())
    assert result[0].tree is None


@pytest.mark.django_db
def test_generate_recommendations_end_to_end(user):
    user.goals = ["fruit", "screening"]
    user.maintenance_level = "low"
    user.experience_level = "beginner"
    user.save()
    TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=15.0,
        maintenance_level="low",
    )
    parcel = Parcel.objects.create(
        user=user, name="Garden", climate_zone="Cfb - Oceanic",
        soil_ph=6.5, soil_drainage="Well-drained", area_m2=200.0,
        latitude=48.85, longitude=2.35,
    )
    llm_response = '[{"scientific_name": "Prunus avium", "rank": 1, "explanation": "Great for your garden"}]'
    with patch("apps.recommendations.services.recommender.get_recommendation", return_value=llm_response):
        result = generate_recommendations(parcel, user)
    assert result[0].scientific_name == "Prunus avium"


@pytest.mark.django_db
def test_parse_recommendations_strips_markdown_code_blocks():
    tree = TreeSpecies.objects.create(
        scientific_name="Prunus avium",
        common_name="Wild Cherry",
        koppen_zones=["Cfb"],
        soil_ph_min=5.5,
        soil_ph_max=7.5,
        primary_use="fruit",
        max_height_m=15.0,
        maintenance_level="low",
    )
    raw_json = '```json\n[{"scientific_name": "Prunus avium", "rank": 1, "explanation": "Great tree"}]\n```'
    result = parse_recommendations(raw_json, TreeSpecies.objects.all())
    assert result[0].tree == tree


@pytest.mark.django_db
def test_parse_recommendations_raises_on_invalid_json():
    with pytest.raises(RecommendationError, match="Failed to parse recommendation response"):
        parse_recommendations("not valid json", TreeSpecies.objects.none())


@pytest.mark.django_db
def test_parse_recommendations_raises_on_missing_keys():
    raw_json = '[{"name": "Oak"}]'
    with pytest.raises(RecommendationError, match="Failed to parse recommendation response"):
        parse_recommendations(raw_json, TreeSpecies.objects.none())


@pytest.mark.django_db
def test_parse_recommendations_raises_on_non_array_json():
    raw_json = '{"recommendations": [{"scientific_name": "Oak"}]}'
    with pytest.raises(RecommendationError, match="Failed to parse recommendation response"):
        parse_recommendations(raw_json, TreeSpecies.objects.none())


@pytest.mark.django_db
def test_generate_recommendations_returns_empty_when_no_compatible_trees(user):
    parcel = Parcel.objects.create(
        user=user, name="Desert", climate_zone="BWh - Hot desert",
        soil_ph=8.5, soil_drainage="Excessive", area_m2=100.0,
        latitude=25.0, longitude=55.0,
    )
    result = generate_recommendations(parcel, user)
    assert result == []
