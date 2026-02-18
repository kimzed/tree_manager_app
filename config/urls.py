from django.contrib import admin
from django.urls import include, path

from apps.users.views import landing

urlpatterns = [
    path("", landing, name="landing"),
    path("admin/", admin.site.urls),
    path("users/", include("apps.users.urls")),
    path("parcels/", include("apps.parcels.urls")),
    path("trees/", include("apps.trees.urls")),
]
