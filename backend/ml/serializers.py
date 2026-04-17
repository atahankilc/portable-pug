from rest_framework import serializers
from .models import MLJob


class MLJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLJob
        fields = ("id", "task_id", "task_type", "status", "result", "created_at")
