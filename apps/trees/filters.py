from __future__ import annotations

from django.db.models import QuerySet

from apps.trees.models import TreeSpecies

SIZE_FILTERS: dict[str, dict[str, float]] = {
    "small": {"max_height_m__lt": 8},
    "medium": {"max_height_m__gte": 8, "max_height_m__lte": 15},
    "large": {"max_height_m__gt": 15},
}


def filter_trees(
    queryset: QuerySet[TreeSpecies],
    *,
    primary_use: str = "",
    size: str = "",
    maintenance_level: str = "",
) -> QuerySet[TreeSpecies]:
    if primary_use:
        queryset = queryset.filter(primary_use=primary_use)
    if size and size in SIZE_FILTERS:
        queryset = queryset.filter(**SIZE_FILTERS[size])
    if maintenance_level:
        queryset = queryset.filter(maintenance_level=maintenance_level)
    return queryset
