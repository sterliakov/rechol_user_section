from __future__ import annotations

from typing import Any

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as _PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm as _PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as _SetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import formhelpers as helpers
from .models import Appellation, OfflineResult, OnlineSubmission, User


class UserCreateFormMixin:
    is_create: bool

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
            'username',
        )

        widgets = {
            'birth_date': DatePickerInput(format='%d/%m/%Y'),
        }

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.fields['birth_date'].input_formats = settings.DATE_INPUT_FORMATS
        self.helper = helpers.UserUpdateFormHelper(is_create=self.is_create)

        if settings.DISABLE_OFFLINE_REG:
            self.fields['venue_selected'].disabled = True

    def clean_city(self):
        return self.cleaned_data['city'].removeprefix('г.').strip()

    def clean(self):
        data = super().clean()

        if self.cleaned_data['actual_form'] > self.cleaned_data['participation_form']:
            self.add_error(
                'participation_form',
                ValidationError(_('Only your form or higher is allowed.'), 'TOO_OLD'),
            )

        if self.cleaned_data['first_name'] == self.cleaned_data['last_name']:
            self.add_error(
                None,
                ValidationError(
                    _('Please fill your name and surname in separate fields.'),
                    'ALL_NAMES_TOGETHER',
                ),
            )

        return data


class UserCreateForm(UserCreateFormMixin, UserCreationForm):
    is_create = True

    def save(self, commit=True):
        u = super().save(commit=False)  # don't save on error
        u.email = self.cleaned_data['email']
        if commit:
            u.save()
        return u


class UserUpdateForm(UserCreateFormMixin, forms.ModelForm):
    is_create = False

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].disabled = True


class JudgeCreateFormMixin:
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'patronymic_name')

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.helper = helpers.JudgeUpdateFormHelper()


class JudgeCreateForm(JudgeCreateFormMixin, UserCreationForm):
    def save(self, commit=True):
        u = super().save(commit=False)  # don't save on error
        u.email = self.cleaned_data['email']
        if commit:
            u.save()
        return u


class JudgeUpdateForm(JudgeCreateFormMixin, forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].disabled = True


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


class OnlineSubmissionForm(forms.ModelForm):
    class Meta:
        model = OnlineSubmission
        fields = ('paper_original', 'comment')

        widgets = {
            'paper_original': forms.ClearableFileInput(
                attrs={'accept': 'application/pdf'}
            )
        }

    def __init__(self, *args: Any, **kwargs: Any):
        contest_over = kwargs.pop('contest_over')
        super().__init__(*args, **kwargs)
        self.helper = helpers.OnlineSubmissionFormHelper()
        if contest_over:
            self.helper.layout = helpers.Layout(*self.helper.layout[:-1])
            for f in self.fields.values():
                f.disabled = True


class OfflineResultDisplayForm(forms.ModelForm):
    class Meta:
        model = OfflineResult
        fields = ('scores', 'final_scores', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.helper = helpers.OfflineResultDisplayFormHelper()
        for f in self.fields.values():
            f.disabled = True


class AppellationForm(forms.ModelForm):
    class Meta:
        model = Appellation
        fields = ('message', 'response')

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.fields['response'].disabled = True
        if self.instance.id:
            self.fields['message'].disabled = True
        else:
            self.fields['response'].widget.attrs['data-display'] = 'none'


AppellationFormset = forms.inlineformset_factory(
    OfflineResult, Appellation, form=AppellationForm, extra=1, can_delete=False
)
AppellationDisplayFormset = forms.inlineformset_factory(
    OfflineResult, Appellation, form=AppellationForm, extra=0, can_delete=False
)
