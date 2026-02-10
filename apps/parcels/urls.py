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
]
