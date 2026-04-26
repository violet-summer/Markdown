import logging
import time
from functools import lru_cache
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class MinioStorage:
    """Thin wrapper for uploading artifacts into a MinIO bucket."""

    def __init__(self) -> None:
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
            region=settings.minio_region,
        )
        self._bucket = settings.minio_bucket
        self._root_prefix = settings.minio_root_prefix.strip("/")
        self._retries = max(1, settings.minio_upload_retries)
        self._ensure_bucket()

    def upload_file(self, local_path: Path, object_name: str) -> str:
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"GLB artifact missing: {local_path}")

        clean_object = self._normalize_object_name(object_name)
        for attempt in range(1, self._retries + 1):
            try:
                self._client.fput_object(self._bucket, clean_object, str(local_path))
                return self._public_url(clean_object)
            except S3Error as exc:
                logging.error(
                    "MinIO upload failed (attempt %s/%s) for %s: %s",
                    attempt,
                    self._retries,
                    clean_object,
                    exc,
                )
            except Exception as exc:  # noqa: BLE001
                logging.exception(
                    "Unexpected error during MinIO upload (attempt %s/%s) for %s",
                    attempt,
                    self._retries,
                    clean_object,
                )
            if attempt < self._retries:
                time.sleep(0.5 * (2 ** (attempt - 1)))
        raise RuntimeError(f"Failed to upload {local_path} to MinIO after {self._retries} attempts")

    def object_name_for(self, relative_path: Path) -> str:
        clean = Path(relative_path).as_posix().lstrip("/")
        if not clean or clean == "assets":
            raise ValueError("Object key must include file path under assets/")
        if not clean.startswith("assets/"):
            raise ValueError(f"Object key must start with assets/: {clean}")
        if self._root_prefix:
            return f"{self._root_prefix}/{clean}"
        return clean

    def _ensure_bucket(self) -> None:
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Unable to access MinIO bucket '{self._bucket}'") from exc

    def _public_url(self, object_name: str) -> str:
        scheme = "https" if settings.minio_secure else "http"
        endpoint = settings.minio_endpoint.rstrip("/")
        return f"{scheme}://{endpoint}/{self._bucket}/{object_name}"

    def _normalize_object_name(self, object_name: str) -> str:
        object_name = object_name.strip("/")
        return object_name.replace("\\", "/")


@lru_cache(maxsize=1)
def get_minio_storage() -> MinioStorage:
    return MinioStorage()
