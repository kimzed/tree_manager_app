from django.urls import path

from apps.trees import views

app_name = "trees"

urlpatterns = [
    path("", views.tree_browse, name="browse"),
    path("filter/", views.tree_list_partial, name="filter"),
]
