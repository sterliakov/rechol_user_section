from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework import permissions

from users.models import User


class IsVenuePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        del view
        user = request.user
        return user.is_authenticated and user.role == User.Roles.VENUE


class IsJudgePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        del view
        user = request.user
        return user.is_authenticated and user.role == User.Roles.JUDGE


class ParticipantMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == User.Roles.PARTICIPANT


class VenueMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == User.Roles.VENUE
