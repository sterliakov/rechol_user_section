from __future__ import annotations

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

        config = ConfigurationSingleton.objects.get()
        if self.role == User.Roles.PARTICIPANT:
            if config.registration_start > timezone.now():
                raise ValidationError(_("Registration not open yet."))
            if timezone.now() > config.registration_end:
                raise ValidationError(_("Registration closed."))
        elif self.role == User.Roles.VENUE:
            if config.venue_registration_start > timezone.now():
                raise ValidationError(_("Registration not open yet."))
            if timezone.now() > config.venue_registration_end:
                raise ValidationError(_("Registration closed."))
        else:
            raise ValidationError(_("Unknown role"))

        # TODO: confirm email
        serializer.save(role=self.role)
        return Response()


class ParticipantProfileView(RetrieveUpdateAPIView):
    serializer_class = serializers.ParticipantProfileSerializer
    permission_classes = (IsParticipant,)

    def get_object(self):
        return self.request.user


class VenueProfileView(RetrieveUpdateAPIView):
    serializer_class = serializers.VenueSerializer
    permission_classes = (IsVenue,)

    def get_object(self):
        return self.request.user.owned_venue


class VenueListView(PublicMixin, ListAPIView):
    queryset = Venue.objects.filter(is_confirmed=True)
    serializer_class = serializers.VenueSerializer


class ConfigView(PublicMixin, RetrieveAPIView):
    serializer_class = serializers.ConfigSerializer

    def get_object(self):
        return ConfigurationSingleton.objects.get()
