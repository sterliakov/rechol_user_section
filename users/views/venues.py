from __future__ import annotations

import io
import logging

from django.http.request import BadRequest
from django.http.response import FileResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from openpyxl import Workbook

from users import forms
from users.models import (
    ConfigurationSingleton,
    OfflineProblem,
    OfflineResult,
    OrganizerCertificate,
    User,
    Venue,
)
from users.permissions import IsVenuePermission, VenueMixin
from users.serializers import ScanUploadSerializer
from users.utils import generate_upload_url

LOG = logging.getLogger(__name__)


class VenueUserRegistrationView(CreateView):
    template_name = "registration.html"
    form_class = forms.JudgeCreateForm

    def get_success_url(self):
        return reverse("profile")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse("profile"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        rsp = super().form_valid(form)
        user = form.instance
        user.role = user.Roles.VENUE
        user.save()
        LOG.info(
            "Registered a venue user: id %s, email %s, name %s",
            user.pk,
            user.email,
            user.get_full_name(),
        )
        return rsp


class VenueRegistrationView(VenueMixin, CreateView):
    model = Venue
    form_class = forms.VenueForm
    template_name = "venue_registration.html"
    success_url = "?success=true"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return HttpResponseRedirect(reverse("venue_user_registration"))

        try:
            request.user.owned_venue  # noqa: B018
        except Venue.DoesNotExist:
            return super().dispatch(request, *args, **kwargs)

        dest = reverse("venue_update")
        if request.GET.get("success"):
            dest += "?success=true"
        return HttpResponseRedirect(dest)

    def get_context_data(self, **kwargs):
        config = ConfigurationSingleton.objects.get()
        return super().get_context_data(**kwargs) | {
            "registration_not_started": config.venue_registration_start > tz.now(),
            "registration_closed": tz.now() > config.venue_registration_end,
            "instance": None,
        }

    def get_form_kwargs(self, **kwargs):
        return super().get_form_kwargs(**kwargs) | {
            "instance": Venue(owner=self.request.user)
        }

    def form_valid(self, form):
        ctx = self.get_context_data()
        if ctx["registration_not_started"]:
            form.add_error(_("Registration not open yet."))
            return self.form_invalid(form)
        if ctx["registration_closed"]:
            form.add_error(_("Registration closed."))
            return self.form_invalid(form)

        return super().form_valid(form)


class VenueUpdateView(VenueMixin, UpdateView):
    model = Venue
    form_class = forms.VenueForm
    template_name = "venue_registration.html"
    success_url = "?success=true"

    def get_object(self, _queryset=None):
        if self.request.user.is_anonymous:
            raise Venue.DoesNotExist
        return self.request.user.owned_venue

    def dispatch(self, request, *args, **kwargs):
        try:
            self.get_object()
        except Venue.DoesNotExist:
            return HttpResponseRedirect(reverse("venue_registration"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        config = ConfigurationSingleton.objects.get()
        return super().get_context_data(**kwargs) | {
            "registration_not_started": config.venue_registration_start > tz.now(),
            "registration_closed": tz.now() > config.venue_registration_end,
            "instance": self.get_object(),
        }


class VenueParticipantsView(VenueMixin, ListView):
    model = User
    template_name = "venue_participants.html"

    def get_queryset(self):
        venue = self.request.user.owned_venue
        return User.objects.filter(
            role=User.Roles.PARTICIPANT, venue_selected=venue
        ).order_by("participation_form", "last_name", "first_name", "id")

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "upload_form": forms.ScanUploadForm(),
            "user_data_form": forms.DummyUserDataForm(),
            "venue": Venue.objects.filter(owner=self.request.user).first(),
        }


class VenueParticipantsDownloadView(VenueMixin, View):
    model = User
    template_name = "venue_participants.html"

    def get_queryset(self):
        venue = self.request.user.owned_venue
        return User.objects.filter(
            role=User.Roles.PARTICIPANT, venue_selected=venue
        ).order_by("participation_form", "last_name", "first_name", "id")

    def get(self, _request):
        users = self.get_queryset()
        columns = [
            _("Last name"),
            _("First name"),
            _("Patronymic name"),
            _("ID number"),
            _("Grade"),
            _("Room"),
            _("Arrived"),
            _("Terminated"),
            _("Exits"),
            _("Pages count"),
            _("Comments"),
        ]
        wb = Workbook()
        ws = wb.active
        ws.append([str(col) for col in columns])
        for user in users:
            ws.append([
                user.last_name,
                user.first_name,
                user.patronymic_name,
                user.passport,
                user.participation_form,
            ])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename="participants.xlsx")


class VenueScanUploadView(generics.CreateAPIView):
    permission_classes = (IsVenuePermission,)
    queryset = OfflineResult.objects.all()
    serializer_class = ScanUploadSerializer
    http_method_names = ["post"]

    def perform_create(self, serializer):
        participant_pk = self.request.GET.get("participant")
        participant = User.objects.get(pk=participant_pk)
        if participant.venue_selected != self.request.user.owned_venue:
            raise BadRequest("Not registered to this venue.")
        serializer.save(user=participant)


class VenueScanStartUploadView(APIView):
    permission_classes = (IsVenuePermission,)
    http_method_names = ["post"]

    def post(self, request):
        upload_to = generate_upload_url(
            str(request.user.pk), OfflineResult.paper_original.field
        )
        return Response(upload_to)


class VenueScanDeleteView(generics.DestroyAPIView):
    permission_classes = (IsVenuePermission,)

    def get_queryset(self):
        return OfflineResult.objects.filter(user__venue_selected=self.venue)

    @property
    def venue(self):
        return self.request.user.owned_venue


class VenueInstructionsView(VenueMixin, TemplateView):
    template_name = "venue_instructions.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "problems": OfflineProblem.objects.filter(visible=True).order_by(
                "target_form"
            ),
            "venue": Venue.objects.filter(owner=self.request.user).first(),
        }


class OrganizerCertificatesListView(VenueMixin, TemplateView):
    template_name = "venue_certificates.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "certificates": self.request.user.owned_venue.certificates.all()
        }


class OrganizerCertificateDownloadView(VenueMixin, DetailView):
    model = OrganizerCertificate

    def get(self, request, pk, **_kwargs):  # noqa: ARG002
        from users.certificates import make_organizer_thanks_cert

        pdf = make_organizer_thanks_cert(self.get_object())
        return FileResponse(pdf, content_type="application/pdf")
