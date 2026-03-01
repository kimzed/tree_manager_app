from __future__ import annotations

from django.db.models import QuerySet

from apps.parcels.models import Parcel
from apps.trees.constants import MOOD_SETS, MoodSet, get_mood_set
from apps.trees.models import TreeSpecies


def _filter_species_for_parcel(
    queryset: QuerySet[TreeSpecies], parcel: Parcel,
) -> QuerySet[TreeSpecies]:
    queryset = queryset.filter(koppen_zones__contains=parcel.climate_zone)
    if parcel.soil_ph is not None:
        queryset = queryset.filter(
            soil_ph_min__lte=parcel.soil_ph,
            soil_ph_max__gte=parcel.soil_ph,
        )
    return queryset


def get_compatible_mood_sets(parcel: Parcel) -> list[tuple[MoodSet, int]]:
    """Return each mood set paired with the count of compatible trees for the given parcel."""
    all_names = {name for mood in MOOD_SETS for name in mood.scientific_names}
    queryset = TreeSpecies.objects.filter(scientific_name__in=all_names)
    compatible_names = set(
        _filter_species_for_parcel(queryset, parcel).values_list("scientific_name", flat=True),
    )
    return [(mood, len(set(mood.scientific_names) & compatible_names)) for mood in MOOD_SETS]


def get_trees_for_mood_set(parcel: Parcel, mood_key: str) -> list[TreeSpecies]:
    """Return compatible trees for a specific mood set and parcel."""
    mood = get_mood_set(mood_key)
    if mood is None:
        return []
    queryset = TreeSpecies.objects.filter(scientific_name__in=mood.scientific_names)
    return list(_filter_species_for_parcel(queryset, parcel))
