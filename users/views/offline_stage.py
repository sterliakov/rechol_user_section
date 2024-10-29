from __future__ import annotations

import logging

from django.http.response import HttpResponseRedirect
from django.utils import timezone as tz
from django.views.generic import UpdateView

from users import forms
from users.models import ConfigurationSingleton, OfflineProblem, OfflineResult
from users.permissions import ParticipantMixin

LOG = logging.getLogger(__name__)


class AppellationView(ParticipantMixin, UpdateView):
    model = OfflineResult
    form_class = forms.OfflineResultDisplayForm
    template_name = "offline_appellation.html"
    success_url = "?success=True"

    def get_object(self, _queryset=None):
        try:
            return self.request.user.offlineresult
        except OfflineResult.DoesNotExist:
            return None

    @property
    def is_open(self):
        config = ConfigurationSingleton.objects.get()
        return config.offline_appeal_start <= tz.now() <= config.offline_appeal_end

    @property
    def was_open(self):
        config = ConfigurationSingleton.objects.get()
        return config.offline_appeal_start <= tz.now()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs) | {
            "object": self.object,
            "is_open": self.is_open,
            "was_open": self.was_open,
            "problems": {
                p.target_form: p for p in OfflineProblem.objects.filter(visible=True)
            },
        }
        if self.object:
            ctx["helper"] = forms.helpers.AppellationFormHelper()
            ctx["messages"] = (
                forms.AppellationFormset
                if self.is_open
                else forms.AppellationDisplayFormset
            )(self.request.POST or None, instance=self.object)
        return ctx

    def form_valid(self, form):
        if not self.is_open:
            return HttpResponseRedirect("/")
        # Doing nothing with form - it's readonly
        if self.object:
            formset = self.get_context_data()["messages"]
            if formset.is_valid():
                formset.save()
            else:
                return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())
