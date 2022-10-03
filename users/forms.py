from __future__ import annotations

from typing import Any

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as _PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm as _PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as _SetPasswordForm

from . import formhelpers as helpers
from .models import User

# from django.contrib.auth.forms import UserCreationForm
# from django.utils.translation import gettext_lazy as _


# class UserForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = User

#     def __init__(self, *args: Any, **kwargs: Any):
#         self.user = kwargs.pop('user', None)
#         choices = (
#             [
#                 (short, perm_name)
#                 for short, perm_name in User.TYPES
#                 if self.user.has_perm(f'users.add_{perm_name}')
#             ]
#             if self.user
#             else []
#         )

#         # not at the top to drop 'user' first
#         super().__init__(*args, **kwargs)

#         self.helper = helpers.UserFormHelper()
#         self.fields['inner_role'] = forms.ChoiceField(choices=choices)
#         self.fields['email'] = forms.EmailField()

#     def save(self, commit: bool = True) -> User:
#         if not commit:
#             raise NotImplementedError('Cannot use commit=False here.')
#         self.clean()
#         u = super().save(commit=False)  # don't save on error
#         # Restore everything non-standart
#         u.inner_role = self.cleaned_data['inner_role']
#         u.email = self.cleaned_data['email']
#         u.username = self.cleaned_data['username']
#         u.created_by = self.user
#         u.clinic = self.user.clinic
#         u.save()
#         return u


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = (
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'created_by',
            'user_permissions',
            'groups',
            'last_login',
            'password',
        )

        widgets = {
            'birth_date': DatePickerInput(format='%d/%m/%Y'),
        }

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.fields['birth_date'].input_formats = settings.DATE_INPUT_FORMATS
        self.helper = helpers.UserUpdateFormHelper()


class LoginForm(AuthenticationForm):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.helper = helpers.LoginFormHelper()


class PasswordResetForm(_PasswordResetForm):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = ''
        self.helper = helpers.PasswordResetFormHelper()


class PasswordChangeForm(_PasswordChangeForm):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.helper = helpers.PasswordChangeFormHelper()


class SetPasswordForm(_SetPasswordForm):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.helper = helpers.SetPasswordFormHelper()
