from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views as views

app_name = "users"

router = DefaultRouter(trailing_slash=True)
router.register("profile", views.ProfileViewSet, "profile")
router.register("venues", views.VenueViewSet, "venue")

urlpatterns = [
    path("", include(router.urls)),
    path("config/", views.ConfigView.as_view(), name="config"),
    path("register/", views.RegisterView.as_view(), name="register"),
]
