from unittest.mock import MagicMock, patch

import pytest
from anthropic.types import TextBlock

from apps.recommendations.services.llm import RecommendationError, get_recommendation
from apps.recommendations.services.prompts import (
    format_recommendation_prompt,
    format_renegotiation_prompt,
    load_prompt,
)


def test_load_prompt_reads_template():
    content = load_prompt("recommendation")
    assert "compatible_trees" in content


def test_format_recommendation_prompt_fills_placeholders():
    result = format_recommendation_prompt(
        user_goals="fruit trees, privacy screening",
        maintenance_level="low",
        experience_level="beginner",
        climate_zone="Cfb - Oceanic",
        soil_ph="6.5",
        soil_drainage="Well-drained",
        parcel_area="450 m²",
        compatible_trees='[{"name": "Prunus avium"}]',
    )
    assert "fruit trees, privacy screening" in result


def test_format_renegotiation_prompt_fills_placeholders():
    result = format_renegotiation_prompt(
        user_goals="shade trees",
        maintenance_level="low",
        experience_level="intermediate",
        climate_zone="Cfb - Oceanic",
        soil_ph="6.5",
        soil_drainage="Well-drained",
        parcel_area="300 m²",
        previous_recommendations='[{"scientific_name": "Quercus robur"}]',
        user_constraint="at least one cherry tree",
        compatible_trees='[{"name": "Prunus avium"}]',
    )
    assert "at least one cherry tree" in result


@patch("apps.recommendations.services.llm.anthropic.Anthropic")
def test_get_recommendation_returns_response(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_message = MagicMock()
    mock_message.content = [TextBlock(type="text", text='[{"scientific_name": "Prunus avium", "rank": 1, "explanation": "Great choice"}]')]
    mock_client.messages.create.return_value = mock_message
    result = get_recommendation("test prompt")
    assert "Prunus avium" in result


@patch("apps.recommendations.services.llm.anthropic.Anthropic")
def test_get_recommendation_raises_on_api_error(mock_anthropic_cls):
    import anthropic as anthropic_mod

    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.side_effect = anthropic_mod.APIError(
        message="Server error",
        request=MagicMock(),
        body=None,
    )
    with pytest.raises(RecommendationError, match="Recommendation service error"):
        get_recommendation("test prompt")


@patch("apps.recommendations.services.llm.anthropic.Anthropic")
def test_get_recommendation_raises_on_timeout(mock_anthropic_cls):
    import anthropic as anthropic_mod

    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.side_effect = anthropic_mod.APITimeoutError(
        request=MagicMock(),
    )
    with pytest.raises(RecommendationError, match="Recommendation service timed out"):
        get_recommendation("test prompt")


@patch("apps.recommendations.services.llm.anthropic.Anthropic")
def test_get_recommendation_raises_on_unexpected_format(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_message = MagicMock()
    mock_message.content = [MagicMock(spec=[])]
    mock_client.messages.create.return_value = mock_message
    with pytest.raises(RecommendationError, match="Unexpected response format"):
        get_recommendation("test prompt")


@pytest.mark.django_db
def test_recommendation_view_returns_error_partial_on_failure(user):
    from django.test import Client as DjangoClient
    from apps.parcels.models import Parcel

    parcel = Parcel.objects.create(
        user=user, name="Garden", area_m2=100.0,
        latitude=48.85, longitude=2.35, climate_zone="Cfb - Oceanic",
    )
    client = DjangoClient()
    client.force_login(user)
    with patch("apps.recommendations.views.get_recommendation", side_effect=RecommendationError("API down")):
        response = client.post(f"/recommendations/{parcel.pk}/generate/")
    assert b"having trouble finding trees" in response.content


@pytest.mark.django_db
def test_recommendation_view_returns_escaped_result_on_success(user):
    from django.test import Client as DjangoClient
    from apps.parcels.models import Parcel

    parcel = Parcel.objects.create(
        user=user, name="Garden", area_m2=100.0,
        latitude=48.85, longitude=2.35, climate_zone="Cfb - Oceanic",
    )
    client = DjangoClient()
    client.force_login(user)
    with patch("apps.recommendations.views.get_recommendation", return_value='[{"scientific_name": "Prunus avium"}]'):
        response = client.post(f"/recommendations/{parcel.pk}/generate/")
    assert b"Prunus avium" in response.content
