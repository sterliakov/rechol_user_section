from __future__ import annotations

from django.urls import path

from users.models import User

from . import api_views as views

app_name = "users"

urlpatterns = [
    path("config/", views.ConfigView.as_view(), name="config"),
    path("venues/", views.VenueListView.as_view(), name="venues"),
    path(
        "register/participant/",
        views.RegisterView.as_view(role=User.Roles.PARTICIPANT),
        name="participant_register",
    ),
    path(
        "profile/participant/",
        views.ParticipantProfileView.as_view(),
        name="participant_profile",
    ),
    path(
        "register/venue/",
        views.RegisterView.as_view(role=User.Roles.VENUE),
        name="venue_register",
    ),
    path("profile/venue/", views.VenueProfileView.as_view(), name="venue_profile"),
]
