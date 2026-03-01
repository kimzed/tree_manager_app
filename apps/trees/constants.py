from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MoodSet:
    key: str
    name: str
    emoji: str
    description: str
    scientific_names: tuple[str, ...]


MOOD_SETS: tuple[MoodSet, ...] = (
    MoodSet(
        key="low-effort-abundance",
        name="Low-Effort Abundance",
        emoji="🍎",
        description="Fruit and nut trees that practically take care of themselves",
        scientific_names=(
            "Corylus avellana",
            "Prunus avium",
            "Prunus cerasus",
            "Prunus domestica",
            "Malus sylvestris",
            "Castanea sativa",
            "Olea europaea",
            "Mespilus germanica",
            "Pyrus pyraster",
            "Ficus carica",
        ),
    ),
    MoodSet(
        key="privacy-fortress",
        name="Privacy Fortress",
        emoji="🏰",
        description="Dense evergreen barriers that block the world out",
        scientific_names=(
            "Taxus baccata",
            "Carpinus betulus",
            "Ilex aquifolium",
            "Cupressus sempervirens",
            "Buxus sempervirens",
            "Thuja occidentalis",
            "Picea abies",
            "Pinus mugo",
            "Viburnum tinus",
            "Ligustrum lucidum",
        ),
    ),
    MoodSet(
        key="pollinator-paradise",
        name="Pollinator Paradise",
        emoji="🐝",
        description="A buffet for bees, butterflies, and birds",
        scientific_names=(
            "Tilia cordata",
            "Crataegus monogyna",
            "Prunus spinosa",
            "Prunus padus",
            "Salix caprea",
            "Sorbus aucuparia",
            "Sambucus nigra",
            "Corylus avellana",
            "Robinia pseudoacacia",
            "Malus sylvestris",
        ),
    ),
    MoodSet(
        key="four-season-beauty",
        name="Four-Season Beauty",
        emoji="🍃",
        description="Year-round visual drama in your garden",
        scientific_names=(
            "Betula pendula",
            "Acer platanoides",
            "Acer campestre",
            "Larix decidua",
            "Cercis siliquastrum",
            "Liquidambar styraciflua",
            "Fagus sylvatica",
            "Koelreuteria paniculata",
            "Arbutus unedo",
            "Ginkgo biloba",
        ),
    ),
    MoodSet(
        key="drought-warriors",
        name="Drought Warriors",
        emoji="🏜️",
        description="Tough trees that thrive in heat and dry spells",
        scientific_names=(
            "Olea europaea",
            "Quercus ilex",
            "Quercus suber",
            "Ceratonia siliqua",
            "Cupressus sempervirens",
            "Punica granatum",
            "Ficus carica",
            "Pinus pinea",
            "Arbutus unedo",
            "Cercis siliquastrum",
        ),
    ),
)


def get_mood_set(key: str) -> MoodSet | None:
    return next((mood for mood in MOOD_SETS if mood.key == key), None)
