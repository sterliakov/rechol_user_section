from __future__ import annotations

from django.views.generic import TemplateView

handler_400 = TemplateView.as_view(template_name="errors/bad_request.html")
handler_403 = TemplateView.as_view(template_name="errors/permission_denied.html")
handler_404 = TemplateView.as_view(template_name="errors/not_found.html")
handler_500 = TemplateView.as_view(template_name="errors/error.html")
