from textwrap import dedent

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.http.response import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from rest_framework import generics

from . import forms
from .models import Annotation, Event
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
