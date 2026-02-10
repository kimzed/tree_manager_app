from django.urls import path

from apps.parcels import views

app_name = "parcels"

urlpatterns = [
    path("create/", views.parcel_create, name="create"),
    path("geocode/", views.geocode_address_view, name="geocode"),
    path("save/", views.parcel_save, name="save"),
]
