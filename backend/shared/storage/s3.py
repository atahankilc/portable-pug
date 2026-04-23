from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


class S3Storage:
    """S3/MinIO-backed Storage. `get_local_path` is unsupported by design —
    cloud consumers fetch via presigned `get_url`."""

    def __init__(
        self,
        *,
        endpoint_url: str | None,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
        ensure_bucket: bool = True,
    ):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        if ensure_bucket:
            self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError as err:
            if err.response.get("Error", {}).get("Code") in {"404", "NoSuchBucket"}:
                self.client.create_bucket(Bucket=self.bucket)
            else:
                raise

    def put(self, key: str, data: BinaryIO, content_type: str) -> str:
        self.client.upload_fileobj(
            data,
            self.bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        return key

    def get_local_path(self, key: str) -> Path:
        raise NotImplementedError(
            "S3Storage has no local path; use get_url() or download explicitly."
        )

    def get_url(self, key: str, ttl: int = 300) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=ttl,
        )

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)
