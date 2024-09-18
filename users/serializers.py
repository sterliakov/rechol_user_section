from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Annotation, ConfigurationSingleton, User, Venue


class AnnotationSerializer(ModelSerializer):
    class Meta:
        model = Annotation
        fields = "__all__"


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["pk", "email", "first_name", "last_name", "role"]


class ParticipantProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "patronymic_name",
            "gender",
            "birth_date",
            "phone",
            "passport",
            "country",
            "city",
            "school",
            "actual_form",
            "participation_form",
            "vk_link",
            "telegram_nickname",
            "venue_selected",
            "online_selected",
        ]

    def validate_city(self, city: str) -> str:
        prefixes = ["г.", "Г.", "город", "Город"]
        city = city.strip()
        for prefix in prefixes:
            city = city.removeprefix(prefix)
        return city.strip()


class RegisterSerializer(ModelSerializer):
    password1 = serializers.CharField(write_only=True, max_length=255)
    password2 = serializers.CharField(write_only=True, max_length=255)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "patronymic_name",
            "password1",
            "password2",
        ]

    def validate(self, attrs):
        res = super().validate(attrs)
        password = res.pop("password1")
        if password != res.pop("password2"):
            raise ValidationError(_("Password fields do not match"))
        return res | {"password": password}

    def save(self, **kwargs):
        password = self.validated_data.pop("password")
        obj = super().save(**kwargs)
        obj.set_password(password)
        obj.save()
        return obj


class VenueSerializer(ModelSerializer):
    class Meta:
        model = Venue
        fields = [
            "id",
            "city",
            "short_name",
            "full_name",
            "full_address",
            "contact_phone",
            "is_full",
            "is_confirmed",
            "confirmation_letter",
        ]


class VenueListSerializer(ModelSerializer):
    class Meta:
        model = Venue
        fields = [
            "id",
            "city",
            "short_name",
            "full_name",
            "full_address",
            "contact_phone",
            "is_full",
        ]


class ConfigSerializer(ModelSerializer):
    class Meta:
        model = ConfigurationSingleton
        fields = [
            "registration_start",
            "registration_end",
            "venue_registration_start",
            "venue_registration_end",
            "offline_appeal_start",
            "offline_appeal_end",
            "online_appeal_start",
            "online_appeal_end",
            "forbid_venue_change",
            "show_offline_problems",
        ]
