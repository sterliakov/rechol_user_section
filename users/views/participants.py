from __future__ import annotations

import logging
from textwrap import dedent

from django.core.mail import send_mail
from django.http.response import (
    FileResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, View

from users import forms
from users.models import ConfigurationSingleton
from users.permissions import ParticipantMixin

LOG = logging.getLogger(__name__)


class RegistrationView(CreateView):
    template_name = "registration.html"
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
        return reverse("profile")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse("profile"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        config = ConfigurationSingleton.objects.get()
        return super().get_context_data(**kwargs) | {
            "registration_not_started": config.registration_start > tz.now(),
            "registration_closed": tz.now() > config.registration_end,
        }

    def form_valid(self, form):
        ctx = self.get_context_data()
        if ctx["registration_not_started"]:
            form.add_error(_("Registration not open yet."))
            return self.form_invalid(form)
        if ctx["registration_closed"]:
            form.add_error(_("Registration closed."))
            return self.form_invalid(form)

        rsp = super().form_valid(form)
        user = form.instance
        send_mail(
            "Регистрация на Проектную химическую олимпиаду",
            self.WELCOME_MAIL.format(
                name=str(user), suffix=("ый" if user.gender == "m" else "ая")
            ),
            None,
            [user.email],
        )
        return rsp


class CertificatesListView(ParticipantMixin, TemplateView):
    template_name = "certificates.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "certificates": self.request.user.get_certificates()
        }


class CertificateDownloadView(ParticipantMixin, View):
    def get(self, request, kind, **_kwargs):
        from users.certificates import make_prelim_offline_cert

        if kind not in request.user.get_certificates():
            return HttpResponseBadRequest("Certificate not issued.")
        match kind:
            case "prelim_offline":
                cert = make_prelim_offline_cert(request.user)
                return FileResponse(cert, content_type="application/pdf")
            case _:
                return HttpResponseBadRequest("Unknown certificate kind.")
