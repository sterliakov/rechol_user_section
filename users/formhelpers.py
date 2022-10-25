from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django.utils.translation import gettext_lazy as _


class CustomFormHelper(FormHelper):
    include_media = False
    html5_required = True
    form_class = ''
    use_custom_control = False


def one_row(fields: dict[str | Field, int | str]) -> Div:
    return Div(
        *[
            (
                Field(f, wrapper_class=(f'col-md-{w or 6}' if w is not ... else 'col'))
                if isinstance(f, str)
                else Div(f, css_class=(f'col-md-{w or 6}' if w is not ... else 'col'))
            )
            for f, w in fields.items()
        ],
        css_class='form-row align-items-stretch',
    )


def selectpicker(field, kwargs=None):
    kwargs = kwargs or {}
    kwargs = {
        'data-style': 'form-control',
    } | kwargs
    return Field(field, css_class='selectpicker', **kwargs)


class LoginFormHelper(CustomFormHelper):
    form_class = 'login_form noasterisks'

    txt = _('Forgot Password?')
    layout = Layout(
        'username',
        'password',
        HTML(
            '<a href="{% url \'password_reset\' %}" '
            f'class="text-right d-block f_14">{txt}</a>'
        ),
        FormActions(
            Div(
                Submit(
                    'submit',
                    _('Login'),
                    css_class='mt-sm-5 mt-4 f_20 submit_btn btn btn-primary',
                ),
                css_class='text-center',
            ),
        ),
    )


class UserUpdateFormHelper(CustomFormHelper):
    form_class = ''

    txt = _('Change password')
    layout = Layout(
        Div(
            Div(Field('email'), css_class='col-12 col-sm-9 order-2 order-sm-1'),
            Div(
                HTML(
                    '<a class="btn btn-primary" '
                    'href="{% url \'password_change\' %}">'
                    f'{txt}</a>'
                ),
                css_class='col-12 col-sm-3 order-1 order-sm-2 prefs-form-btn',
            ),
            css_class='form-row',
        ),
        one_row(
            {
                'first_name': '4 col-sm-12 col-lg-4',
                'last_name': '4 col-sm-12 col-lg-4',
                'patronymic_name': '4 col-sm-12 col-lg-4',
            }
        ),
        one_row(
            {
                'passport': '4 col-sm-12 col-lg-4',
                'birth_date': '4 col-sm-12 col-lg-4',
                selectpicker('gender'): '4 col-sm-12 col-lg-4',
            }
        ),
        one_row(
            {
                'city': '4 col-sm-12 col-lg-4',
                'school': '4 col-sm-12 col-lg-4',
                'phone': '4 col-sm-12 col-lg-4',
            }
        ),
        one_row(
            {
                'password1': '6 col-sm-12 col-lg-6',
                'password2': '6 col-sm-12 col-lg-6',
            }
        ),
        one_row(
            {
                'vk_link': '6 col-sm-12 col-lg-6',
                'telegram_nickname': '6 col-sm-12 col-lg-6',
            }
        ),
        one_row(
            {
                selectpicker('actual_form'): '6 col-sm-12 col-lg-6',
                selectpicker('participation_form'): '6 col-sm-12 col-lg-6',
            }
        ),
        one_row(
            {
                selectpicker(
                    'venue_selected',
                    {
                        'data-live-search': 'true',
                        'data-container': 'body',
                        'data-mobile': 'true',
                    },
                ): '6 col-sm-12 col-lg-6',
                Div(
                    Field('online_selected', template='checkbox_field.html'),
                    css_class=(
                        'custom-control custom-checkbox'
                        ' d-flex h-100 pb-4 align-items-end'
                    ),
                ): '6 col-sm-12 col-lg-6',
            },
        ),
        FormActions(
            Div(Submit('submit', _('Save'), css_class='my-3'), css_class='text-center'),
        ),
    )


class UserFormHelper(CustomFormHelper):
    layout = Layout(
        'email',
        'password1',
        'password2',
        'username',
        'inner_role',
        FormActions(
            Div(Submit('submit', _('Save'), css_class='mt-3'), css_class='text-center'),
        ),
    )


class JudgeUpdateFormHelper(CustomFormHelper):
    layout = Layout(
        'email',
        'password1',
        'password2',
        'first_name',
        'last_name',
        'patronymic_name',
        FormActions(
            Div(Submit('submit', _('Save'), css_class='mt-3'), css_class='text-center'),
        ),
    )


class PasswordResetFormHelper(CustomFormHelper):
    form_class = 'login_form noasterisks'

    txt = _('Back to login')
    layout = Layout(
        'email',
        FormActions(
            Div(
                Submit(
                    'submit',
                    _('Continue'),
                    css_class='mt-4 f_20 submit_btn btn btn-primary',
                ),
                css_class='text-center',
            ),
        ),
        HTML(
            '<a href="{% url \'login\' %}" '
            f'class="text-center d-block f_14 mt-3">{txt}</a>'
        ),
    )


class PasswordChangeFormHelper(CustomFormHelper):
    form_class = 'login_form noasterisks'
    layout = Layout(
        'old_password',
        'new_password1',
        'new_password2',
        FormActions(
            Div(
                Submit(
                    'submit',
                    _('Change'),
                    css_class='mt-4 f_20 submit_btn btn btn-primary',
                ),
                css_class='text-center',
            ),
        ),
    )


class SetPasswordFormHelper(CustomFormHelper):
    form_class = 'login_form noasterisks'
    layout = Layout(
        'new_password1',
        'new_password2',
        FormActions(
            Div(
                Submit(
                    'submit',
                    _('Set password'),
                    css_class='mt-4 f_20 submit_btn btn btn-primary',
                ),
                css_class='text-center',
            ),
        ),
    )


class OnlineSubmissionFormHelper(CustomFormHelper):
    form_class = 'login_form noasterisks'
    layout = Layout(
        'file',
        'comment',
        FormActions(
            Div(
                Submit(
                    'submit',
                    _('Submit'),
                    css_class='mt-4 f_20 submit_btn btn btn-primary',
                ),
                css_class='text-center',
            ),
        ),
    )
