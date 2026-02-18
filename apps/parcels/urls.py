from django.urls import path

from apps.parcels import views

app_name = "parcels"

urlpatterns = [
    path("", views.parcel_list, name="list"),
    path("create/", views.parcel_create, name="create"),
    path("geocode/", views.geocode_address_view, name="geocode"),
    path("save/", views.parcel_save, name="save"),
    path("<int:pk>/", views.parcel_detail, name="detail"),
    path("<int:pk>/edit/", views.parcel_edit, name="edit"),
    path("<int:pk>/update/", views.parcel_update, name="update"),
    path("<int:pk>/analyze/", views.parcel_analyze, name="analyze"),
    path("<int:pk>/full-analyze/", views.parcel_full_analyze, name="full-analyze"),
    path("<int:pk>/soil-analyze/", views.parcel_soil_analyze, name="soil-analyze"),
    path("<int:pk>/soil-skip/", views.parcel_soil_skip, name="soil-skip"),
]
