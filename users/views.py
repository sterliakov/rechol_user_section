from textwrap import dedent

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from . import forms
from .models import Event


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'personal.html'
    form_class = forms.UserUpdateForm
    success_url = '#'

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


class IndexView(ListView):
    model = Event
    template_name = 'index.html'
    ordering = ['start']
