from __future__ import annotations

from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit


class CustomFormHelper(FormHelper):
    include_media = False
    html5_required = True
    form_class = ""
    use_custom_control = False


def one_row(fields: dict[str | Field, int | str]) -> Div:
    return Div(
        *[
            (
                Field(f, wrapper_class=(f"col-md-{w or 6}" if w is not ... else "col"))
                if isinstance(f, str)
                else Div(f, css_class=(f"col-md-{w or 6}" if w is not ... else "col"))
            )
            for f, w in fields.items()
        ],
        css_class="form-row align-items-stretch",
    )


def selectpicker(field, live_search=False, kwargs=None):
    kwargs = {
        "data-style": "form-control",
        "data-container": "body",
    } | (kwargs or {})
    if live_search:
        kwargs["data-live-search"] = "true"
    return Field(field, css_class="selectpicker", **kwargs)


def autosize(field: str):
    return Field(field, css_class="autosize")


class LoginFormHelper(CustomFormHelper):
    form_class = "login_form noasterisks"

    txt = _("Forgot Password?")
    layout = Layout(
        "username",
        "password",
        HTML(
            "<a href=\"{% url 'password_reset' %}\" "
            f'class="text-right d-block f_14">{txt}</a>',
        ),
        FormActions(
            Div(
                Submit(
                    "submit",
                    _("Login"),
                    css_class="mt-sm-5 mt-4 f_20 submit_btn btn btn-primary",
                ),
                css_class="text-center",
            ),
        ),
    )


class UserUpdateFormHelper(CustomFormHelper):
    form_class = ""

    base_layout_1 = [
        one_row(
            {
                "first_name": "4 col-sm-12 col-lg-4",
                "last_name": "4 col-sm-12 col-lg-4",
                "patronymic_name": "4 col-sm-12 col-lg-4",
            },
        ),
        one_row(
            {
                "passport": "4 col-sm-12 col-lg-4",
                "birth_date": "4 col-sm-12 col-lg-4",
                selectpicker("gender"): "4 col-sm-12 col-lg-4",
            },
        ),
        one_row(
            {
                selectpicker("country", live_search=True): "6 col-sm-12 col-lg-6",
                "city": "6 col-sm-12 col-lg-6",
            },
        ),
        one_row(
            {
                "school": "8 col-sm-12 col-lg-8",
                "phone": "4 col-sm-12 col-lg-4",
            },
        ),
    ]
    base_layout_2 = [
        one_row(
            {
                selectpicker("actual_form"): "6 col-sm-12 col-lg-6",
                selectpicker("participation_form"): "6 col-sm-12 col-lg-6",
            },
        ),
        one_row(
            {
                "vk_link": "6 col-sm-12 col-lg-6",
                "telegram_nickname": "6 col-sm-12 col-lg-6",
            },
        ),
        one_row(
            {
                selectpicker(
                    "venue_selected",
                    live_search=True,
                ): "6 col-sm-12 col-lg-6",
                Div(
                    Field("online_selected", template="checkbox_field.html"),
                    css_class=(
                        "custom-control custom-checkbox"
                        " d-flex h-100 pt-4 mt-3 align-items-start"
                    ),
                ): "6 col-sm-12 col-lg-6",
            },
        ),
        FormActions(
            Div(Submit("submit", _("Save"), css_class="my-3"), css_class="text-center"),
        ),
    ]

    def __init__(self, *args, is_create, **kwargs):
        super().__init__(*args, **kwargs)
        if is_create:
            email_div = Div(
                Div(Field("email"), css_class="col-12 order-1"),
                css_class="form-row",
            )
            passwords_row = one_row(
                {
                    "password1": "6 col-sm-12 col-lg-6",
                    "password2": "6 col-sm-12 col-lg-6",
                },
            )
            self.layout = Layout(
                email_div,
                *self.base_layout_1,
                passwords_row,
                *self.base_layout_2,
            )
        else:
            txt = _("Change password")
            email_div = Div(
                Div(Field("email"), css_class="col-12 col-sm-9 order-2 order-sm-1"),
                Div(
                    HTML(
                        '<a class="btn btn-primary" '
                        "href=\"{% url 'password_change' %}\">"
                        f"{txt}</a>",
                    ),
                    css_class="col-12 col-sm-3 order-1 order-sm-2 prefs-form-btn",
                ),
                css_class="form-row",
            )
            self.layout = Layout(
                email_div,
                *self.base_layout_1,
                *self.base_layout_2,
            )


class UserFormHelper(CustomFormHelper):
    layout = Layout(
        "email",
        "password1",
        "password2",
        "username",
        "inner_role",
        FormActions(
            Div(Submit("submit", _("Save"), css_class="mt-3"), css_class="text-center"),
        ),
    )


class JudgeUpdateFormHelper(CustomFormHelper):
    layout = Layout(
        "email",
        "password1",
        "password2",
        "first_name",
        "last_name",
        "patronymic_name",
        FormActions(
            Div(Submit("submit", _("Save"), css_class="mt-3"), css_class="text-center"),
        ),
    )


class VenueFormHelper(CustomFormHelper):
    use_custom_control = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        txt = _("Download template")
        file_url = static("files/venue_letter_template.docx")
        self.layout = Layout(
            "city",
            "full_name",
            "short_name",
            "full_address",
            "contact_phone",
            Div(
                Div(Field("confirmation_letter"), css_class="col-12 col-md-6 col-lg-9"),
                Div(
                    HTML(
                        '<a class="btn btn-primary" style="margin-top: 2rem !important"'
                        f' href="{file_url}">{txt}</a>',
                    ),
                    css_class="col-12 col-md-6 col-lg-3",
                ),
                css_class="form-row",
            ),
            FormActions(
                Div(
                    Submit("submit", _("Save"), css_class="mt-3"),
                    css_class="text-center",
                ),
            ),
        )


class PasswordResetFormHelper(CustomFormHelper):
    form_class = "login_form noasterisks"

    txt = _("Back to login")
    layout = Layout(
        "email",
        FormActions(
            Div(
                Submit(
                    "submit",
                    _("Continue"),
                    css_class="mt-4 f_20 submit_btn btn btn-primary",
                ),
                css_class="text-center",
            ),
        ),
        HTML(
            "<a href=\"{% url 'login' %}\" "
            f'class="text-center d-block f_14 mt-3">{txt}</a>',
        ),
    )


class PasswordChangeFormHelper(CustomFormHelper):
    form_class = "login_form noasterisks"
    layout = Layout(
        "old_password",
        "new_password1",
        "new_password2",
        FormActions(
            Div(
                Submit(
                    "submit",
                    _("Change"),
                    css_class="mt-4 f_20 submit_btn btn btn-primary",
                ),
                css_class="text-center",
            ),
        ),
    )


class SetPasswordFormHelper(CustomFormHelper):
    form_class = "login_form noasterisks"
    layout = Layout(
        "new_password1",
        "new_password2",
        FormActions(
            Div(
                Submit(
                    "submit",
                    _("Set password"),
                    css_class="mt-4 f_20 submit_btn btn btn-primary",
                ),
                css_class="text-center",
            ),
        ),
    )


class OnlineSubmissionFormHelper(CustomFormHelper):
    form_class = "login_form noasterisks"
    use_custom_control = True

    layout = Layout(
        "paper_original",
        "comment",
        FormActions(
            Div(
                Submit(
                    "submit",
                    _("Submit"),
                    css_class="mt-4 f_20 submit_btn btn btn-primary",
                ),
                css_class="text-center",
            ),
        ),
    )


class OnlineSubmissionDisplayFormHelper(CustomFormHelper):
    form_class = "login_form noasterisks"
    use_custom_control = True
    field_class = "input-group"

    layout = Layout(
        "scores",
        "final_scores",
        "paper_original",
        autosize("comment"),
    )


class OfflineResultDisplayFormHelper(CustomFormHelper):
    form_class = "login_form noasterisks"
    use_custom_control = True

    layout = Layout(
        "scores",
        "final_scores",
        autosize("comment"),
    )


class AppellationFormHelper(CustomFormHelper):
    use_custom_control = True
    form_tag = False

    layout = Layout(
        autosize("message"),
        autosize("response"),
    )


class ScanUploadFormHelper(CustomFormHelper):
    use_custom_control = True
    layout = Layout(
        "paper_original",
        FormActions(
            Div(
                Submit("submit", _("Upload"), css_class="mt-3"),
                css_class="text-center",
            ),
        ),
    )


class DummyUserDataFormHelper(CustomFormHelper):
    use_custom_control = True
    layout = Layout(
        "first_name",
        "last_name",
        "patronymic_name",
        "participation_form",
    )
