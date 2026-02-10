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
