import pytest
from django.test import Client
from apps.trees.models import TreeSpecies


@pytest.fixture
def logged_in_client(user):
    client = Client()
    client.login(username="testuser", password="SecurePass123!")
    return client


@pytest.fixture
def fruit_tree(db):
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
def ornamental_tree(db):
    return TreeSpecies.objects.create(
        scientific_name="Betula pendula",
        common_name="Silver Birch",
        koppen_zones=["Cfb"],
        soil_ph_min=4.5,
        soil_ph_max=7.0,
        primary_use="ornamental",
        max_height_m=12.0,
        maintenance_level="low",
    )


@pytest.mark.django_db
def test_tree_browse_renders_page(logged_in_client, fruit_tree):
    response = logged_in_client.get("/trees/")
    assert response.templates[0].name == "trees/browse.html"


@pytest.mark.django_db
def test_tree_list_partial_filters(logged_in_client, fruit_tree, ornamental_tree):
    response = logged_in_client.get("/trees/filter/?type=fruit")
    assert list(response.context["trees"]) == [fruit_tree]


@pytest.mark.django_db
def test_tree_list_partial_includes_count(logged_in_client, fruit_tree, ornamental_tree):
    response = logged_in_client.get("/trees/filter/?type=fruit")
    assert response.context["count"] == 1
