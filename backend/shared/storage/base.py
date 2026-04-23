from pathlib import Path
from typing import BinaryIO, Protocol, runtime_checkable


@runtime_checkable
class Storage(Protocol):
    """Object-storage interface used by core_api (writer) and ai_api (reader).

    Implementations: LocalFileStorage (sidecar/desktop), S3Storage (cloud/MinIO).
    """

    def put(self, key: str, data: BinaryIO, content_type: str) -> str:
        """Persist bytes from a file-like object under `key`. Returns the key."""

    def get_local_path(self, key: str) -> Path:
        """Return a filesystem path for direct reads. Only valid for backends
        where data lives on a local volume (sidecar mode)."""

    def get_url(self, key: str, ttl: int = 300) -> str:
        """Return a URL the caller can fetch. Presigned for S3, file:// for local."""

    def delete(self, key: str) -> None:
        """Remove the object. No-op if missing."""
