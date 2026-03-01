from apps.trees.constants import MOOD_SETS, get_mood_set
from apps.trees.models import TreeSpecies


def test_get_mood_set_by_key():
    mood = get_mood_set("low-effort-abundance")
    assert (mood.name, mood.emoji) == ("Low-Effort Abundance", "🍎")


def test_get_mood_set_unknown_returns_none():
    assert get_mood_set("nonexistent") is None


def test_mood_sets_unique_species_count():
    unique_names = {name for mood in MOOD_SETS for name in mood.scientific_names}
    assert len(unique_names) == 43


def test_all_mood_set_species_exist_in_database(mood_set_species):
    all_names = {name for mood in MOOD_SETS for name in mood.scientific_names}
    assert TreeSpecies.objects.filter(scientific_name__in=all_names).count() == len(all_names)
