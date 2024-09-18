from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response

UserModel = get_user_model()
LOG = logging.getLogger(__name__)


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Reimplements `rest_frameworks.views.exception_handler`.

    Differs in `ValidationError` treatment: wraps with ``errors`` and
    ``non_field_errors``.

    This is necessary to return errors in a fixed format, as defined in
    ``api/schema.py``.
    """
    from rest_framework.views import set_rollback  # cycle

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        if exc.status_code == status.HTTP_400_BAD_REQUEST and (
            request := context.get("request")
        ):
            LOG.info("Full request payload: %s", request.data)

        headers = {}
        if auth_header := getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = auth_header
        if wait := getattr(exc, "wait", None):
            headers["Retry-After"] = f"{wait:d}"

        if isinstance(exc.detail, dict):
            non_field_errors = exc.detail.pop("non_field_errors", [])
            data = {
                "errors": exc.detail,
                "non_field_errors": non_field_errors,
            }
        elif isinstance(exc.detail, list):
            data = {
                "errors": {},
                "non_field_errors": exc.detail,
            }
        else:
            data = {"detail": exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
