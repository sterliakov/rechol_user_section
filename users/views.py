from __future__ import annotations

import contextlib
import io
from textwrap import dedent

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.http.response import (
    FileResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.functional import cached_property
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

from openpyxl import Workbook

from . import forms
from .models import (
    Annotation,
    ConfigurationSingleton,
    Event,
    OfflineProblem,
    OfflineResult,
    OnlineProblem,
    OnlineSubmission,
    OrganizerCertificate,
    User,
    Venue,
)
from .serializers import AnnotationSerializer


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


class RegistrationView(CreateView):
    template_name = "registration.html"
    form_class = forms.UserCreateForm

    WELCOME_MAIL = dedent(
        """
        Уважаем{suffix} {name}!

        Вы успешно зарегистрировались на Проектную химическую олимпиаду.
        Сайт олимпиады: https://chemolymp.ru/
        Личный кабинет: https://profile.chemolymp.ru/

        В личном кабинете Вы можете изменить площадку выполнения заданий очного
        отборочного тура, а позже - принять участие в заочном туре.

        По всем вопросам Вы можете связаться с нами через электронную почту
        info@chemolymp.ru

        С уважением,
        Оргкомитет Проектной химической олимпиады
    """,
    )

    def get_success_url(self):
        return reverse("profile")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse("profile"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        config = ConfigurationSingleton.objects.get()
        return super().get_context_data(**kwargs) | {
            "registration_not_started": config.registration_start > tz.now(),
            "registration_closed": tz.now() > config.registration_end,
        }

    def form_valid(self, form):
        ctx = self.get_context_data()
        if ctx["registration_not_started"]:
            form.add_error(_("Registration not open yet."))
            return self.form_invalid(form)
        if ctx["registration_closed"]:
            form.add_error(_("Registration closed."))
            return self.form_invalid(form)

        rsp = super().form_valid(form)
        user = form.instance
        send_mail(
            "Регистрация на Проектную химическую олимпиаду",
            self.WELCOME_MAIL.format(
                name=str(user),
                suffix=("ый" if user.gender == "m" else "ая"),
            ),
            None,
            [user.email],
        )
        return rsp


class JudgeRegistrationView(CreateView):
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
        user.role = user.Roles.JUDGE
        user.is_staff = True
        user.is_active = False
        user.save()
        return rsp


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
        return rsp


class IndexView(ListView):
    model = Event
    template_name = "index.html"
    ordering = ["start"]


class AnnotationList(LoginRequiredMixin, generics.ListCreateAPIView):
    serializer_class = AnnotationSerializer

    def post(self, request, *args, **kwargs):
        if request.user.role != request.user.Roles.JUDGE:
            return HttpResponseForbidden(
                _("You do not have access to editing annotations"),
            )
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        filename = self.request.query_params.get("filename")
        page = self.request.query_params.get("page")
        qs = Annotation.objects.filter(filename=filename)
        if page:
            qs = qs.filter(page=int(page))
        return qs


class AnnotationDetail(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def test_func(self):
        return self.request.user.role == self.request.user.Roles.JUDGE

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have access to the requested resource")


class OnlineStageListView(LoginRequiredMixin, ListView):
    model = OnlineProblem
    template_name = "online.html"
    ordering = ["opens"]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_anonymous:
            return qs.none()
        if user.role == user.Roles.PARTICIPANT:
            qs = qs.filter(target_form=user.participation_form, visible=True)

        qs = list(qs)
        for problem in qs:
            problem.real_end = tz.now() + problem.get_remaining_time(user)
            sub = problem.onlinesubmission_set.filter(user=user).first()
            problem.was_started = sub is not None
            problem.was_submitted = sub and sub.is_submitted
            problem.is_open = not sub or sub.remaining_time.total_seconds() >= 0

        return qs


class ProblemDispatchMixin(LoginRequiredMixin):
    @cached_property
    def problem(self):
        if not self.request.user.is_authenticated:
            return None
        return OnlineProblem.objects.get(
            id=int(self.kwargs["problem_pk"]),
            target_form=self.request.user.participation_form,
        )

    def dispatch(self, *args, **kwargs):
        try:
            self.problem  # noqa: B018
        except OnlineProblem.DoesNotExist:
            return HttpResponseRedirect(
                reverse("online_submission_index") + "?error=DENIED",
            )
        return super().dispatch(*args, **kwargs)


class OnlineStageStartView(ProblemDispatchMixin, DetailView):
    model = OnlineSubmission
    template_name = "online_start.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "problem": self.problem,
            "has_ended": self.object and self.object.remaining_time.total_seconds() < 0,
        }

    def get_object(self, _queryset=None):
        return self.request.user.onlinesubmission_set.filter(
            problem=self.problem,
        ).first()

    def post(self, *_args, **kwargs):
        if not self.problem.is_open_now_for_user(self.request.user):
            return HttpResponseRedirect(
                reverse("online_submission_index") + "?error=GONE",
            )

        with contextlib.suppress(Exception):
            # Someone's trying to open twice, what for?
            self.request.user.onlinesubmission_set.create(
                problem=self.problem,
                started=tz.now(),
            )

        return HttpResponseRedirect(reverse("online_submission_update", kwargs=kwargs))


class OnlineStageSubmitView(ProblemDispatchMixin, UpdateView):
    model = OnlineSubmission
    form_class = forms.OnlineSubmissionForm
    template_name = "online_submission.html"
    success_url = "?success=true"

    @property
    def problem(self):
        return OnlineProblem.objects.get(id=int(self.kwargs["problem_pk"]))

    @property
    def is_over(self):
        return bool(
            not self.problem.is_open_now_for_user(self.request.user)
            or self.object.remaining_time.total_seconds() < 0,
        )

    def get_object(self, _queryset=None):
        return self.request.user.onlinesubmission_set.get(problem=self.problem)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        try:
            self.object = self.get_object()
        except (
            OnlineSubmission.DoesNotExist,
            OnlineProblem.DoesNotExist,
            AttributeError,
        ):
            # AttributeError on AnonymousUser: LoginRequiredMixin affects super.dispatch
            # and is not checked yet
            return HttpResponseRedirect(
                reverse("online_submission_start", kwargs=kwargs),
            )

        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        if self.is_over:
            return HttpResponseBadRequest(
                _("Cannot submit solutions to closed contest."),
            )
        return super().post(*args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"contest_over": self.is_over}

    def get_context_data(self, **kwargs):
        config = ConfigurationSingleton.objects.get()
        # Check only for start time, the page remains available when appeal is closed
        appeal_open = config.online_appeal_start <= tz.now()

        return super().get_context_data(**kwargs) | {
            "contest_over": self.is_over,
            "appeal_open": appeal_open,
        }


class AppellationView(LoginRequiredMixin, UpdateView):
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

        return super().form_valid(form)


class OnlineAppellationView(LoginRequiredMixin, UpdateView):
    model = OnlineSubmission
    form_class = forms.OnlineSubmissionDisplayForm
    template_name = "online_appellation.html"
    success_url = "?success=True"

    def get_object(self, _queryset=None):
        try:
            return self.request.user.onlinesubmission_set.get(
                problem_id=int(self.kwargs["problem_pk"]),
            )
        except OnlineSubmission.DoesNotExist:
            return None

    @cached_property
    def is_open(self):
        config = ConfigurationSingleton.objects.get()
        return config.online_appeal_start <= tz.now() <= config.online_appeal_end

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs) | {
            "object": self.object,
            "is_open": self.is_open,
        }
        if self.object:
            ctx["helper"] = forms.helpers.AppellationFormHelper()
            ctx["messages"] = (
                forms.OnlineAppellationFormset
                if self.is_open
                else forms.OnlineAppellationDisplayFormset
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

        return super().form_valid(form)


class VenueRegistrationView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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

    def test_func(self):
        return self.request.user.role == User.Roles.VENUE

    def get_form_kwargs(self, **kwargs):
        return super().get_form_kwargs(**kwargs) | {
            "instance": Venue(owner=self.request.user),
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


class VenueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Venue
    form_class = forms.VenueForm
    template_name = "venue_registration.html"
    success_url = "?success=true"

    def get_object(self, _queryset=None):
        if self.request.user.is_anonymous:
            return None
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

    def test_func(self):
        return self.request.user.role == User.Roles.VENUE


class VenuesListView(ListView):
    queryset = Venue.objects.filter(is_confirmed=True)
    model = Venue
    template_name = "venues_list.html"
    ordering = ["city"]


class VenueParticipantsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "venue_participants.html"

    def test_func(self):
        return self.request.user.role == User.Roles.VENUE

    def get_queryset(self):
        owner = self.request.user
        if owner.is_anonymous:
            return User.objects.none()
        try:
            venue = owner.owned_venue
        except Venue.DoesNotExist:
            return User.objects.none()

        return User.objects.filter(
            role=User.Roles.PARTICIPANT,
            venue_selected=venue,
        ).order_by("participation_form", "last_name", "first_name", "id")

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "upload_form": forms.ScanUploadForm(),
            "user_data_form": forms.DummyUserDataForm(),
            "venue": Venue.objects.filter(owner=self.request.user).first(),
        }


class VenueParticipantsDownloadView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = User
    template_name = "venue_participants.html"

    def test_func(self):
        return self.request.user.role == User.Roles.VENUE

    def get_queryset(self):
        venue = self.request.user.owned_venue
        return User.objects.filter(
            role=User.Roles.PARTICIPANT,
            venue_selected=venue,
        ).order_by("participation_form", "last_name", "first_name", "id")

    def get(self, _request):
        users = self.get_queryset()
        columns = [
            _("Name"),
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
            ws.append([user.get_full_name(), user.passport, user.participation_form])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename="participants.xlsx")


class VenueScanUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = OfflineResult
    form_class = forms.ScanUploadForm
    template_name = "venue_participants.html"

    def get_success_url(self):
        return reverse("venue_participants")

    def test_func(self):
        return self.request.user.role == User.Roles.VENUE

    @property
    def venue(self):
        owner = self.request.user
        if owner.is_anonymous:
            return None
        try:
            return owner.owned_venue
        except Venue.DoesNotExist:
            return None

    def get_form_kwargs(self, **kwargs):
        participant_pk = self.request.GET.get("participant")
        participant = User.objects.get(pk=participant_pk)
        if participant.venue_selected != self.venue:
            return HttpResponseForbidden("Not registered to this venue.")
        return super().get_form_kwargs(**kwargs) | {
            "instance": OfflineResult(user=participant),
        }


class VenueScanDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    generics.DestroyAPIView,
):
    def test_func(self):
        return self.request.user.role == User.Roles.VENUE

    def get_queryset(self):
        if not self.venue:
            return OfflineResult.objects.none()
        return OfflineResult.objects.filter(user__venue_selected=self.venue)

    @property
    def venue(self):
        owner = self.request.user
        if owner.is_anonymous:
            return None
        try:
            return owner.owned_venue
        except Venue.DoesNotExist:
            return None


class VenueInstructionsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "venue_instructions.html"

    def test_func(self):
        return self.request.user.role == User.Roles.VENUE

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "problems": OfflineProblem.objects.filter(visible=True).order_by(
                "target_form",
            ),
            "venue": Venue.objects.filter(owner=self.request.user).first(),
        }


class CertificatesListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "certificates.html"

    def test_func(self):
        return self.request.user.role == User.Roles.PARTICIPANT

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "certificates": self.request.user.get_certificates(),
        }


class CertificateDownloadView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == User.Roles.PARTICIPANT

    def get(self, request, kind, **_kwargs):
        from users.certificates import make_prelim_offline_cert

        if kind not in request.user.get_certificates():
            return HttpResponseBadRequest("Certificate not issued.")
        match kind:
            case "prelim_offline":
                cert = make_prelim_offline_cert(request.user)
                return FileResponse(cert, content_type="application/pdf")
            case _:
                return HttpResponseBadRequest("Unknown certificate kind.")


class OrganizerCertificatesListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    TemplateView,
):
    template_name = "venue_certificates.html"

    def test_func(self):
        return self.request.user.role == User.Roles.VENUE

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "certificates": self.request.user.owned_venue.certificates.all(),
        }


class OrganizerCertificateDownloadView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DetailView,
):
    model = OrganizerCertificate

    def test_func(self):
        return self.request.user.role == User.Roles.VENUE

    def get(self, request, pk, **_kwargs):  # noqa: ARG002
        from users.certificates import make_organizer_thanks_cert

        pdf = make_organizer_thanks_cert(self.get_object())
        return FileResponse(pdf, content_type="application/pdf")
