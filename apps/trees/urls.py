from django.urls import path

from apps.trees import views

app_name = "trees"

urlpatterns = [
    path("", views.tree_browse, name="browse"),
    path("filter/", views.tree_list_partial, name="filter"),
    path(
        "parcels/<int:parcel_id>/mood-sets/",
        views.mood_sets_for_parcel,
        name="mood_sets",
    ),
    path(
        "parcels/<int:parcel_id>/mood-sets/<str:mood_key>/",
        views.mood_set_trees,
        name="mood_set_trees",
    ),
]
