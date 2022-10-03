from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView

# from .models import User
from . import forms


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'personal.html'
    form_class = forms.UserUpdateForm
    success_url = '#'

    def get_object(self):
        return self.request.user
