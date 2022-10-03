from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from . import forms
from .models import Event


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'personal.html'
    form_class = forms.UserUpdateForm
    success_url = '#'

    def get_object(self):
        return self.request.user


class IndexView(ListView):
    model = Event
    template_name = 'index.html'
