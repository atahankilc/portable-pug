from django.conf import settings
from rest_framework import serializers

from .models import Image


class ImageUploadSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)

    def validate(self, attrs):
        data = self.initial_data
        files = getattr(data, "getlist", lambda _k: [])("file")
        if len(files) > 1:
            raise serializers.ValidationError(
                {"file": "Only one file per request is allowed."}
            )
        return attrs

    def validate_file(self, value):
        if value.size > settings.IMAGE_MAX_BYTES:
            raise serializers.ValidationError(
                f"File exceeds max size ({settings.IMAGE_MAX_BYTES} bytes)."
            )
        if value.content_type not in settings.IMAGE_ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                f"Unsupported content type: {value.content_type}."
            )
        return value


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = (
            "id",
            "storage_key",
            "content_type",
            "size_bytes",
            "status",
            "result",
            "created_at",
        )
        read_only_fields = fields
