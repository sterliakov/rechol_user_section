import contextlib
from textwrap import dedent

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.http.response import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from rest_framework import generics

from . import forms
from .models import (
    Annotation,
    ConfigurationSingleton,
    Event,
    OfflineResult,
    OnlineProblem,
    OnlineSubmission,
)
from .serializers import AnnotationSerializer


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'personal.html'
    success_url = '#'

    def get_form_class(self):
        if self.request.user.role == self.request.user.Roles.JUDGE:
            return forms.JudgeUpdateForm
        return forms.UserUpdateForm

    def get_object(self):
        return self.request.user


class RegistrationView(CreateView):
    template_name = 'registration.html'
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
    """
    )

    def get_success_url(self):
        return reverse('profile')

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse('profile'))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse('profile'))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        rsp = super().form_valid(form)
        user = form.instance
        send_mail(
            'Регистрация на Проектную химическую олимпиаду',
            self.WELCOME_MAIL.format(
                name=str(user),
                suffix=('ый' if user.gender == 'm' else 'ая'),
            ),
            None,
            [user.email],
        )
        return rsp


class JudgeRegistrationView(CreateView):
    template_name = 'registration.html'
    form_class = forms.JudgeCreateForm

    def get_success_url(self):
        return reverse('profile')

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse('profile'))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse('profile'))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        rsp = super().form_valid(form)
        user = form.instance
        user.role = user.Roles.JUDGE
        user.is_staff = True
        user.save()
        return rsp


class IndexView(ListView):
    model = Event
    template_name = 'index.html'
    ordering = ['start']


class AnnotationList(LoginRequiredMixin, generics.ListCreateAPIView):
    # queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def post(self, request, *args, **kwargs):
        if request.user.role != request.user.Roles.JUDGE:
            return HttpResponseForbidden(
                _('You do not have access to editing annotations')
            )
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        filename = self.request.query_params.get('filename')
        page = self.request.query_params.get('page')
        qs = Annotation.objects.filter(filename=filename)
        if page:
            qs = qs.filter(page=int(page))
        return qs


class AnnotationDetail(
    LoginRequiredMixin, UserPassesTestMixin, generics.RetrieveUpdateDestroyAPIView
):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def test_func(self):
        return self.request.user.role != self.request.user.Roles.JUDGE


class OnlineStageListView(LoginRequiredMixin, ListView):
    model = OnlineProblem
    template_name = 'online.html'
    ordering = ['opens']

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
        return OnlineProblem.objects.get(
            id=int(self.kwargs['problem_pk']),
            target_form=self.request.user.participation_form,
        )

    def dispatch(self, *args, **kwargs):
        try:
            self.problem
        except OnlineProblem.DoesNotExist:
            return HttpResponseRedirect(
                reverse('online_submission_index') + '?error=DENIED'
            )
        return super().dispatch(*args, **kwargs)


class OnlineStageStartView(ProblemDispatchMixin, DetailView):
    model = OnlineSubmission
    template_name = 'online_start.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            'problem': self.problem,
            'has_ended': self.object and self.object.remaining_time.total_seconds() < 0,
        }

    def get_object(self, queryset=None):
        return self.request.user.onlinesubmission_set.filter(
            problem=self.problem
        ).first()

    def post(self, *args, **kwargs):
        if not self.problem.is_open_now():
            return HttpResponseRedirect(
                reverse('online_submission_index') + '?error=GONE'
            )

        with contextlib.suppress(Exception):
            # Someone's trying to open twice, what for?
            self.request.user.onlinesubmission_set.create(
                problem=self.problem,
                started=tz.now(),
            )

        return HttpResponseRedirect(reverse('online_submission_update', kwargs=kwargs))


class OnlineStageSubmitView(ProblemDispatchMixin, UpdateView):
    model = OnlineSubmission
    form_class = forms.OnlineSubmissionForm
    template_name = 'online_submission.html'
    success_url = '?success=true'

    @cached_property
    def problem(self):
        return OnlineProblem.objects.get(id=int(self.kwargs['problem_pk']))

    @cached_property
    def is_over(self):
        return bool(
            not self.problem.is_open_now()
            or self.object.remaining_time.total_seconds() < 0
        )

    def get_object(self, queryset=None):
        return self.request.user.onlinesubmission_set.get(problem=self.problem)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        try:
            self.object = self.get_object()
        except (OnlineSubmission.DoesNotExist, OnlineProblem.DoesNotExist):
            return HttpResponseRedirect(
                reverse('online_submission_start', kwargs=kwargs)
            )

        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        if self.is_over:
            return HttpResponseBadRequest(
                _('Cannot submit solutions to closed contest.')
            )
        return super().post(*args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'contest_over': self.is_over}

    def get_context_data(self, **kwargs):
        config = ConfigurationSingleton.objects.get()
        # Check only for start time, the page remains available when appeal is closed
        appeal_open = config.online_appeal_start <= tz.now()

        return super().get_context_data(**kwargs) | {
            'contest_over': self.is_over,
            'appeal_open': appeal_open,
        }


class AppellationView(LoginRequiredMixin, UpdateView):
    model = OfflineResult
    form_class = forms.OfflineResultDisplayForm
    template_name = 'offline_appellation.html'
    success_url = '?success=True'

    def get_object(self, queryset=None):
        try:
            return self.request.user.offlineresult
        except OfflineResult.DoesNotExist:
            return None

    @cached_property
    def is_open(self):
        config = ConfigurationSingleton.objects.get()
        return config.offline_appeal_start <= tz.now() <= config.offline_appeal_end

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs) | {
            'object': self.object,
            'is_open': self.is_open,
        }
        if self.object:
            ctx['helper'] = forms.helpers.AppellationFormHelper()
            ctx['messages'] = (
                forms.AppellationFormset
                if self.is_open
                else forms.AppellationDisplayFormset
            )(self.request.POST or None, instance=self.object)
        return ctx

    def form_valid(self, form):
        if not self.is_open:
            return HttpResponseRedirect('/')
        # Doing nothing with form - it's readonly
        if self.object:
            formset = self.get_context_data()['messages']
            if formset.is_valid():
                formset.save()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)


class OnlineAppellationView(LoginRequiredMixin, UpdateView):
    model = OnlineSubmission
    form_class = forms.OnlineSubmissionDisplayForm
    template_name = 'online_appellation.html'
    success_url = '?success=True'

    def get_object(self, queryset=None):
        try:
            return self.request.user.onlinesubmission_set.get(
                problem_id=int(self.kwargs['problem_pk'])
            )
        except OnlineSubmission.DoesNotExist:
            return None

    @cached_property
    def is_open(self):
        config = ConfigurationSingleton.objects.get()
        return config.online_appeal_start <= tz.now() <= config.online_appeal_end

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs) | {
            'object': self.object,
            'is_open': self.is_open,
        }
        if self.object:
            ctx['helper'] = forms.helpers.AppellationFormHelper()
            ctx['messages'] = (
                forms.OnlineAppellationFormset
                if self.is_open
                else forms.OnlineAppellationDisplayFormset
            )(self.request.POST or None, instance=self.object)
        return ctx

    def form_valid(self, form):
        if not self.is_open:
            return HttpResponseRedirect('/')
        # Doing nothing with form - it's readonly
        if self.object:
            formset = self.get_context_data()['messages']
            if formset.is_valid():
                formset.save()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)
