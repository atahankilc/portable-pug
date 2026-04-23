import hashlib
import hmac
import logging
import os
from functools import lru_cache

import httpx
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from shared.storage import Storage, get_storage

logger = logging.getLogger(__name__)
router = APIRouter()


@lru_cache(maxsize=1)
def _storage() -> Storage:
    return get_storage()


class ProcessRequest(BaseModel):
    image_id: str
    storage_key: str
    content_type: str


def _require_internal_token(token: str | None) -> None:
    expected = os.environ.get("INTERNAL_TOKEN", "")
    if not expected or not token or not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Internal-Token",
        )


def _read_bytes(storage: Storage, key: str) -> bytes:
    try:
        path = storage.get_local_path(key)
        return path.read_bytes()
    except NotImplementedError:
        url = storage.get_url(key, ttl=300)
        with httpx.Client(timeout=30) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.content


@router.post("/process")
def process_image(
    payload: ProcessRequest,
    x_internal_token: str | None = Header(default=None, alias="X-Internal-Token"),
):
    _require_internal_token(x_internal_token)

    logger.info(
        "process.start",
        extra={"image_id": payload.image_id, "storage_key": payload.storage_key},
    )

    data = _read_bytes(_storage(), payload.storage_key)
    digest = hashlib.sha256(data).hexdigest()

    result = {
        "image_id": payload.image_id,
        "bytes_read": len(data),
        "sha256": digest,
        "model": "placeholder-v0",
        "labels": [],
    }

    logger.info(
        "process.done",
        extra={"image_id": payload.image_id, "bytes_read": len(data)},
    )
    return result
