import pytest
from apps.parcels.models import Parcel


@pytest.mark.django_db
def test_parcel_str_uses_name(user):
    parcel = Parcel.objects.create(user=user, name="My Garden")
    assert str(parcel) == "My Garden"


@pytest.mark.django_db
def test_parcel_str_fallback_without_name(user):
    parcel = Parcel.objects.create(user=user)
    assert str(parcel) == f"Parcel {parcel.pk}"


@pytest.mark.django_db
def test_parcel_belongs_to_user(user):
    parcel = Parcel.objects.create(user=user, latitude=48.85, longitude=2.35)
    assert parcel.user == user


# --- Story 2.6: Parcel profile property tests ---


@pytest.mark.django_db
def test_has_complete_profile_true_when_all_fields_set(user):
    parcel = Parcel.objects.create(
        user=user, climate_zone="Cfb - Oceanic", soil_ph=6.5, soil_drainage="Well-drained",
    )
    assert parcel.has_complete_profile is True


@pytest.mark.django_db
def test_has_complete_profile_false_when_soil_ph_missing(user):
    parcel = Parcel.objects.create(
        user=user, climate_zone="Cfb - Oceanic", soil_drainage="Well-drained",
    )
    assert parcel.has_complete_profile is False


@pytest.mark.django_db
def test_has_partial_profile_true_when_climate_set_but_soil_missing(user):
    parcel = Parcel.objects.create(
        user=user, climate_zone="Cfb - Oceanic",
    )
    assert parcel.has_partial_profile is True
