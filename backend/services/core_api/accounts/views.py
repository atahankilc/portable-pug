import base64
import hashlib
import logging

from cryptography.hazmat.primitives import serialization
from django.conf import settings
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import permissions, serializers, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer

logger = logging.getLogger(__name__)


class RegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


def _b64url_uint(value: int) -> str:
    byte_length = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(
        value.to_bytes(byte_length, "big")
    ).rstrip(b"=").decode("ascii")


_JWKSResponse = inline_serializer(
    name="JWKSResponse",
    fields={
        "keys": serializers.ListField(child=serializers.DictField()),
    },
)


@extend_schema(
    tags=["auth"],
    responses=_JWKSResponse,
    examples=[
        OpenApiExample(
            "Single RSA key",
            value={
                "keys": [
                    {
                        "kty": "RSA",
                        "use": "sig",
                        "alg": "RS256",
                        "kid": "abcd1234",
                        "n": "…",
                        "e": "AQAB",
                    }
                ]
            },
            response_only=True,
        )
    ],
)
class JWKSView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, _request):
        pem = settings.JWT_PUBLIC_KEY.encode() if settings.JWT_PUBLIC_KEY else b""
        if not pem:
            return Response({"keys": []})
        public_key = serialization.load_pem_public_key(pem)
        numbers = public_key.public_numbers()
        kid = hashlib.sha256(pem).hexdigest()[:16]
        jwk = {
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": kid,
            "n": _b64url_uint(numbers.n),
            "e": _b64url_uint(numbers.e),
        }
        return Response({"keys": [jwk]}, status=status.HTTP_200_OK)
