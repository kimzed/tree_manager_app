import pytest
from django.test import Client
from django.urls import reverse

from apps.parcels.models import Parcel


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(username="mooduser", password="testpass")


@pytest.fixture
def logged_client(user):
    client = Client()
    client.login(username="mooduser", password="testpass")
    return client


@pytest.fixture
def parcel_cfb(user, mood_set_species):
    return Parcel.objects.create(
        user=user,
        name="Test parcel",
        climate_zone="Cfb - Oceanic",
        soil_ph=6.5,
    )


def test_mood_sets_for_parcel_view_returns_cards(logged_client, parcel_cfb):
    url = reverse("trees:mood_sets", kwargs={"parcel_id": parcel_cfb.pk})
    response = logged_client.get(url)

    assert b"Low-Effort Abundance" in response.content


def test_mood_set_trees_view_returns_filtered_list(logged_client, parcel_cfb):
    url = reverse("trees:mood_set_trees", kwargs={
        "parcel_id": parcel_cfb.pk,
        "mood_key": "low-effort-abundance",
    })
    response = logged_client.get(url)

    assert b"trees found" in response.content


def test_mood_set_trees_view_invalid_key_returns_404(logged_client, parcel_cfb):
    url = reverse("trees:mood_set_trees", kwargs={
        "parcel_id": parcel_cfb.pk,
        "mood_key": "nonexistent-mood",
    })
    response = logged_client.get(url)

    assert response.status_code == 404
