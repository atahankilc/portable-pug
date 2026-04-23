import logging
import uuid
from functools import lru_cache

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.logging import request_id_var
from shared.storage import Storage, get_storage

from .models import Image
from .serializers import ImageSerializer, ImageUploadSerializer

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _storage() -> Storage:
    return get_storage()


class ImageUploadView(APIView):
    parser_classes = (MultiPartParser,)

    @extend_schema(
        tags=["images"],
        request=ImageUploadSerializer,
        responses={201: ImageSerializer},
    )
    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload = serializer.validated_data["file"]

        storage_key = f"images/{uuid.uuid4().hex}"
        upload.seek(0)
        _storage().put(storage_key, upload, upload.content_type)

        image = Image.objects.create(
            owner=request.user,
            storage_key=storage_key,
            content_type=upload.content_type,
            size_bytes=upload.size,
        )
        logger.info(
            "image.uploaded",
            extra={
                "image_id": str(image.id),
                "owner_id": request.user.id,
                "size_bytes": image.size_bytes,
                "content_type": image.content_type,
                "storage_key": storage_key,
            },
        )
        return Response(
            ImageSerializer(image).data, status=status.HTTP_201_CREATED
        )


class ImageProcessView(APIView):
    """Dispatch image to ai_api for processing, persist result, return to client."""

    @extend_schema(
        tags=["images"],
        request=None,
        responses={200: ImageSerializer, 502: ImageSerializer},
    )
    def post(self, request, image_id):
        image = get_object_or_404(Image, id=image_id, owner=request.user)

        image.status = Image.Status.PROCESSING
        image.save(update_fields=("status",))

        payload = {
            "image_id": str(image.id),
            "storage_key": image.storage_key,
            "content_type": image.content_type,
        }
        headers = {
            "X-Internal-Token": settings.INTERNAL_TOKEN,
            "X-Request-ID": request_id_var.get() or "",
            "Content-Type": "application/json",
        }
        logger.info(
            "image.process.dispatch",
            extra={"image_id": str(image.id), "ai_api_url": settings.AI_API_URL},
        )
        try:
            resp = requests.post(
                f"{settings.AI_API_URL}/process",
                json=payload,
                headers=headers,
                timeout=settings.AI_PROCESS_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            result = resp.json()
        except requests.RequestException as exc:
            image.status = Image.Status.FAILED
            image.result = {"error": str(exc)}
            image.save(update_fields=("status", "result"))
            logger.exception(
                "image.process.failed", extra={"image_id": str(image.id)}
            )
            return Response(
                ImageSerializer(image).data,
                status=status.HTTP_502_BAD_GATEWAY,
            )

        image.status = Image.Status.READY
        image.result = result
        image.save(update_fields=("status", "result"))
        logger.info(
            "image.process.done", extra={"image_id": str(image.id)}
        )
        return Response(ImageSerializer(image).data)
