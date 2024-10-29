from __future__ import annotations

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView

from users import forms
from users.models import Event, User, Venue

LOG = logging.getLogger(__name__)


class IndexView(ListView):
    model = Event
    template_name = "index.html"
    ordering = ["start"]


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "personal.html"
    success_url = "#"

    def get_form_class(self):
        if self.request.user.role == self.request.user.Roles.JUDGE:
            return forms.JudgeUpdateForm
        return forms.UserUpdateForm

    def get_object(self):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == User.Roles.VENUE:
            return HttpResponseRedirect(reverse("venue_registration"))
        return super().dispatch(request, *args, **kwargs)


class VenuesListView(ListView):
    queryset = Venue.objects.filter(is_confirmed=True)
    model = Venue
    template_name = "venues_list.html"
    ordering = ["city"]
