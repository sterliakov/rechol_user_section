from __future__ import annotations

import logging

from django.db import IntegrityError, transaction
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, UpdateView

from users import forms
from users.models import ConfigurationSingleton, OnlineProblem, OnlineSubmission
from users.permissions import ParticipantMixin
from users.utils import generate_upload_url

LOG = logging.getLogger(__name__)


class OnlineStageListView(ParticipantMixin, ListView):
    model = OnlineProblem
    template_name = "online.html"
    ordering = ["opens"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            super()
            .get_queryset()
            .filter(target_form=user.participation_form, visible=True)
        )

        qs = list(qs)
        for problem in qs:
            problem.real_end = tz.now() + problem.get_remaining_time(user)
            sub = problem.onlinesubmission_set.filter(user=user).first()
            problem.was_started = sub is not None
            problem.was_submitted = sub and sub.is_submitted
            problem.is_open = not sub or sub.remaining_time.total_seconds() >= 0

        return qs


class ProblemDispatchMixin(ParticipantMixin):
    @cached_property
    def problem(self):
        if not self.request.user.is_authenticated:
            raise OnlineProblem.DoesNotExist
        return OnlineProblem.objects.get(
            id=int(self.kwargs["problem_pk"]),
            target_form=self.request.user.participation_form,
        )

    def dispatch(self, *args, **kwargs):
        try:
            self.problem  # noqa: B018
        except OnlineProblem.DoesNotExist:
            return HttpResponseRedirect(
                reverse("online_submission_index") + "?error=DENIED"
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
            problem=self.problem
        ).first()

    def post(self, *_args, **kwargs):
        if not self.problem.is_open_now_for_user(self.request.user):
            return HttpResponseRedirect(
                reverse("online_submission_index") + "?error=GONE"
            )
        LOG.info("Starting online submission for %s", self.request.user.email)

        try:
            with transaction.atomic():
                self.request.user.onlinesubmission_set.create(
                    problem=self.problem, started=tz.now()
                )
        except IntegrityError:
            # Someone's trying to open twice, what for?
            LOG.warning(
                "Attempted to start a submission twice. User: %s, problem: %s",
                self.request.user.email,
                self.problem.pk,
            )

        return HttpResponseRedirect(reverse("online_submission_update", kwargs=kwargs))


class OnlineStageSubmitView(ProblemDispatchMixin, UpdateView):
    model = OnlineSubmission
    form_class = forms.OnlineSubmissionForm
    template_name = "online_submission.html"
    success_url = "?success=true"

    @property
    def is_over(self):
        return bool(
            not self.problem.is_open_now_for_user(self.request.user)
            or self.object.remaining_time.total_seconds() < 0
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
            # AttributeError on AnonymousUser: ParticipantMixin affects super.dispatch
            # and is not checked yet
            return HttpResponseRedirect(
                reverse("online_submission_start", kwargs=kwargs)
            )

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, problem_pk: str):
        del problem_pk
        if self.is_over:
            LOG.warning("Late submission attempted by user %s", request.user.email)
            return HttpResponseBadRequest(
                _("Cannot submit solutions to closed contest.")
            )
        form = self.get_form()
        if form.is_valid():
            LOG.info("Submission by user %s accepted.", request.user.email)
            return self.form_valid(form)
        LOG.warning(
            "Submission by user %s rejected: %s.", request.user.email, form.errors
        )
        return HttpResponseBadRequest("Submission failed")

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"contest_over": self.is_over}

    def get_context_data(self, **kwargs):
        config = ConfigurationSingleton.objects.get()
        # Check only for start time, the page remains available when appeal is closed
        appeal_open = config.online_appeal_start <= tz.now()

        upload_to = generate_upload_url(
            str(self.request.user.pk), OnlineSubmission.paper_original.field
        )

        return super().get_context_data(**kwargs) | {
            "contest_over": self.is_over,
            "appeal_open": appeal_open,
            "upload_to": upload_to,
        }


class OnlineAppellationView(ParticipantMixin, UpdateView):
    model = OnlineSubmission
    form_class = forms.OnlineSubmissionDisplayForm
    template_name = "online_appellation.html"
    success_url = "?success=True"

    def get_object(self, _queryset=None):
        try:
            return self.request.user.onlinesubmission_set.get(
                problem_id=int(self.kwargs["problem_pk"])
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

        return HttpResponseRedirect(self.get_success_url())