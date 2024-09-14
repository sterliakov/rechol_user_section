from __future__ import annotations

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users import serializers
from users.models import ConfigurationSingleton, User, Venue
from users.permissions import IsParticipant


class PublicMixin:
    authentication_classes = ()
    permission_classes = (AllowAny,)


class ProfileViewSet(GenericViewSet):
    queryset = User.objects.filter(role=User.Roles.PARTICIPANT)
    serializer_class = serializers.ParticipantProfileSerializer
    permission_classes = (IsParticipant,)

    @action(methods=["GET"], detail=False)
    def me(self, request):
        return Response(self.get_serializer(request.user).data)


class RegisterView(PublicMixin, APIView):
    def post(self, request):
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        config = ConfigurationSingleton.objects.get()
        if config.registration_start > timezone.now():
            raise ValidationError(_("Registration not open yet."))
        if timezone.now() > config.registration_end:
            raise ValidationError(_("Registration closed."))

        # TODO: confirm email
        serializer.save(role=User.Roles.PARTICIPANT)
        return Response()


class VenueViewSet(PublicMixin, GenericViewSet, ListModelMixin):
    queryset = Venue.objects.filter(is_confirmed=True)
    serializer_class = serializers.VenueSerializer


class ConfigView(PublicMixin, APIView):
    def get(self, request):
        del request
        config = ConfigurationSingleton.objects.get()
        return Response(serializers.ConfigSerializer(config).data)
