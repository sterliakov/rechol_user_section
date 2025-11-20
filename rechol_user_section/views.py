from __future__ import annotations

from django.template.response import TemplateResponse
from django.views.generic import TemplateView


class TemplateResponseBadRequest(TemplateResponse):
    status_code = 400


class TemplateResponsePermissionDenied(TemplateResponse):
    status_code = 403


class TemplateResponseNotFound(TemplateResponse):
    status_code = 404


class TemplateResponseError(TemplateResponse):
    status_code = 500


handler_400 = TemplateView.as_view(
    response_class=TemplateResponseBadRequest, template_name="errors/bad_request.html"
)
handler_403 = TemplateView.as_view(
    response_class=TemplateResponsePermissionDenied,
    template_name="errors/permission_denied.html",
)
handler_404 = TemplateView.as_view(
    response_class=TemplateResponseNotFound, template_name="errors/not_found.html"
)
handler_500 = TemplateView.as_view(
    response_class=TemplateResponseError, template_name="errors/error.html"
)
