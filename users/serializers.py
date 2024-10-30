from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Annotation, OfflineResult, OnlineSubmission


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = "__all__"


class FileUploadSerializer(serializers.Serializer):
    uploaded_to = serializers.CharField(write_only=True)

    _file_field_name: str

    def _validate_prefix(self, prefix):
        if prefix != str(self.context["request"].user.pk):
            raise serializers.ValidationError("File not owned.")

    @property
    def _file_field(self):
        return getattr(self.Meta.model, self._file_field_name).field

    def validate_uploaded_to(self, uploaded_to):
        field = self._file_field

        try:
            _s, _s, prefix, _s = uploaded_to.split("/")
        except ValueError as exc:
            raise serializers.ValidationError(_("Unexpected filename shape")) from exc
        self._validate_prefix(prefix)

        try:
            field.storage.open(uploaded_to.removeprefix(field.storage.location + "/"))
        except FileNotFoundError as exc:
            raise serializers.ValidationError(_("File not found.")) from exc

        return uploaded_to

    def save(self, *args, **kwargs):
        uploaded_to = self.validated_data.pop("uploaded_to")
        instance = super().save(*args, **kwargs)
        filename = uploaded_to.removeprefix(self._file_field.storage.location + "/")
        getattr(instance, self._file_field_name).name = filename
        instance.save()
        return instance


class ScanUploadSerializer(FileUploadSerializer, serializers.ModelSerializer):
    _file_field_name = "paper_original"

    class Meta:
        model = OfflineResult
        fields = ("uploaded_to", "id")
        extra_kwargs = {"id": {"read_only": True}}


class OnlineSubmissionSerializer(FileUploadSerializer, serializers.ModelSerializer):
    _file_field_name = "paper_original"

    class Meta:
        model = OnlineSubmission
        fields = ("uploaded_to", "comment")
