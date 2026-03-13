"""Storage backends for file upload/download."""

from __future__ import annotations

import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Protocol, runtime_checkable

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol defining the storage interface."""

    async def upload(self, file_data: bytes, file_name: str, content_type: str) -> str:
        """Upload a file and return the storage path/key."""
        ...

    async def download(self, storage_path: str) -> bytes:
        """Download a file by its storage path."""
        ...

    async def delete(self, storage_path: str) -> bool:
        """Delete a file. Returns True on success."""
        ...

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get a (possibly pre-signed) URL for the file."""
        ...


class LocalStorage:
    """Local filesystem storage backend."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, storage_path: str) -> Path:
        return self.base_dir / storage_path

    async def upload(self, file_data: bytes, file_name: str, content_type: str) -> str:
        ext = Path(file_name).suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"
        # Organize into year/month directories
        from datetime import datetime
        now = datetime.utcnow()
        sub_dir = self.base_dir / str(now.year) / f"{now.month:02d}"
        sub_dir.mkdir(parents=True, exist_ok=True)

        file_path = sub_dir / unique_name
        file_path.write_bytes(file_data)

        storage_path = str(file_path.relative_to(self.base_dir))
        logger.info("Local upload: %s (%d bytes)", storage_path, len(file_data))
        return storage_path

    async def download(self, storage_path: str) -> bytes:
        file_path = self._resolve_path(storage_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")
        return file_path.read_bytes()

    async def delete(self, storage_path: str) -> bool:
        file_path = self._resolve_path(storage_path)
        if file_path.exists():
            file_path.unlink()
            logger.info("Local delete: %s", storage_path)
            return True
        return False

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        # For local storage, return a relative path; the API serves it
        return f"/api/v1/documents/file/{storage_path}"


class S3Storage:
    """AWS S3 storage backend."""

    def __init__(
        self,
        bucket_name: str | None = None,
        region: str | None = None,
    ) -> None:
        self.bucket_name = bucket_name or settings.AWS_BUCKET_NAME
        self.region = region or settings.AWS_REGION
        self._client = boto3.client("s3", region_name=self.region)

    async def upload(self, file_data: bytes, file_name: str, content_type: str) -> str:
        ext = Path(file_name).suffix
        unique_key = f"uploads/{uuid.uuid4().hex}{ext}"

        try:
            self._client.put_object(
                Bucket=self.bucket_name,
                Key=unique_key,
                Body=file_data,
                ContentType=content_type,
            )
            logger.info("S3 upload: s3://%s/%s (%d bytes)", self.bucket_name, unique_key, len(file_data))
            return unique_key
        except ClientError:
            logger.exception("S3 upload failed for %s", file_name)
            raise

    async def download(self, storage_path: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self.bucket_name, Key=storage_path)
            return response["Body"].read()
        except ClientError:
            logger.exception("S3 download failed for %s", storage_path)
            raise FileNotFoundError(f"S3 object not found: {storage_path}")

    async def delete(self, storage_path: str) -> bool:
        try:
            self._client.delete_object(Bucket=self.bucket_name, Key=storage_path)
            logger.info("S3 delete: s3://%s/%s", self.bucket_name, storage_path)
            return True
        except ClientError:
            logger.exception("S3 delete failed for %s", storage_path)
            return False

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        try:
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": storage_path},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError:
            logger.exception("Failed to generate presigned URL for %s", storage_path)
            raise


def get_storage_backend() -> StorageBackend:
    """Factory function to get the configured storage backend."""
    if settings.STORAGE_BACKEND == "s3":
        return S3Storage()
    return LocalStorage()
