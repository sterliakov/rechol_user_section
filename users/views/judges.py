from __future__ import annotations

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from rest_framework import generics

from users import forms
from users.models import Annotation
from users.permissions import IsJudgePermission
from users.serializers import AnnotationSerializer

LOG = logging.getLogger(__name__)


class JudgeRegistrationView(CreateView):
    template_name = "registration.html"
    form_class = forms.JudgeCreateForm

    def get_success_url(self):
        return reverse("profile")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse("profile"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        rsp = super().form_valid(form)
        user = form.instance
        user.role = user.Roles.JUDGE
        user.is_staff = True
        user.is_active = False
        user.save()
        LOG.info(
            "Registered a judge: id %s, email %s, name %s",
            user.pk,
            user.email,
            user.get_full_name(),
        )
        return rsp


class AnnotationList(LoginRequiredMixin, generics.ListCreateAPIView):
    serializer_class = AnnotationSerializer
    permission_classes = (IsJudgePermission,)

    def get_queryset(self):
        filename = self.request.query_params.get("filename")
        page = self.request.query_params.get("page")
        qs = Annotation.objects.filter(filename=filename)
        if page:
            qs = qs.filter(page=int(page))
        return qs


class AnnotationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer
    permission_classes = (IsJudgePermission,)

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have access to the requested resource")
