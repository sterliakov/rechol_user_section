from __future__ import annotations

from django.contrib.auth import login as session_login
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import ConfigurationSingleton, User, Venue
from users.permissions import IsParticipant, IsVenue


class PublicMixin:
    authentication_classes = ()
    permission_classes = (AllowAny,)


class RegisterView(PublicMixin, APIView):
    role: User.Roles | None = None

    def post(self, request):
        assert self.role is not None
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: confirm email
        user = serializer.save(role=self.role)
        session_login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        return Response()


class ParticipantProfileView(RetrieveUpdateAPIView):
    serializer_class = serializers.ParticipantProfileSerializer
    permission_classes = (IsParticipant,)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        config = ConfigurationSingleton.objects.get()
        now = timezone.now()
        if config.registration_start > now:
            raise ValidationError(_("Registration not open yet."))
        if now > config.registration_end:
            raise ValidationError(_("Registration closed."))
        return super().perform_update(serializer)


class VenueProfileView(RetrieveUpdateAPIView):
    serializer_class = serializers.VenueSerializer
    permission_classes = (IsVenue,)

    def get_object(self):
        venue, _ = Venue.objects.get_or_create(owner=self.request.user)
        return venue

    def perform_update(self, serializer):
        config = ConfigurationSingleton.objects.get()
        now = timezone.now()
        if config.venue_registration_start > now:
            raise ValidationError(_("Registration not open yet."))
        if now > config.venue_registration_end:
            raise ValidationError(_("Registration closed."))

        return super().perform_update(serializer)


class VenueListView(PublicMixin, ListAPIView):
    queryset = Venue.objects.filter(is_confirmed=True)
    serializer_class = serializers.VenueListSerializer


class ConfigView(PublicMixin, RetrieveAPIView):
    serializer_class = serializers.ConfigSerializer

    def get_object(self):
        return ConfigurationSingleton.objects.get()
