from django.contrib.auth.mixins import LoginRequiredMixin
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


class IndexView(ListView):
    model = Event
    template_name = 'index.html'
    ordering = ['start']
