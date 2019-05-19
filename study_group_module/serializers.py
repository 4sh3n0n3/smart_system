# main Group serializer
from rest_framework import serializers

from .models import StudyGroup


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGroup
        fields = '__all__'

