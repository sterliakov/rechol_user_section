from __future__ import annotations

from django.shortcuts import render


def any_method_template_view(template_name, status):
    def view(request):
        return render(request, template_name, status=status)

    return view


handler_400 = any_method_template_view("errors/bad_request.html", 400)
handler_403 = any_method_template_view("errors/permission_denied.html", 403)
handler_404 = any_method_template_view("errors/not_found.html", 404)
handler_500 = any_method_template_view("errors/error.html", 500)
