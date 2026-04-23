import os

from .base import Storage
from .local import LocalFileStorage


def get_storage() -> Storage:
    """Return a Storage implementation based on `STORAGE_BACKEND` env var.

    STORAGE_BACKEND=local (default): LocalFileStorage under STORAGE_ROOT.
    STORAGE_BACKEND=s3:              S3Storage against S3_ENDPOINT/S3_BUCKET.
    """
    backend = os.environ.get("STORAGE_BACKEND", "local").lower()
    if backend == "local":
        root = os.environ.get("STORAGE_ROOT", "./media")
        return LocalFileStorage(root=root)
    if backend == "s3":
        from .s3 import S3Storage

        return S3Storage(
            endpoint_url=os.environ.get("S3_ENDPOINT") or None,
            access_key=os.environ["S3_ACCESS_KEY"],
            secret_key=os.environ["S3_SECRET_KEY"],
            bucket=os.environ["S3_BUCKET"],
            region=os.environ.get("S3_REGION", "us-east-1"),
        )
    raise ValueError(f"Unknown STORAGE_BACKEND: {backend!r}")


__all__ = ["Storage", "LocalFileStorage", "get_storage"]
