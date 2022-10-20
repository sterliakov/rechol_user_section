from rest_framework.serializers import ModelSerializer

from .models import Annotation


class AnnotationSerializer(ModelSerializer):
    class Meta:
        model = Annotation
        fields = '__all__'
