from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.permissions import BasePermission

from users.models import User

if TYPE_CHECKING:
    from rest_framework.request import Request


class IsParticipant(BasePermission):
    """Allows access only to teachers."""

    def has_permission(self, request: Request, _view):
        user = request.user
        return user.is_authenticated and user.role == User.Roles.PARTICIPANT
