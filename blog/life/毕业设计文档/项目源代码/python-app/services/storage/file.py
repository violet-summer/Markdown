import logging
import time
import os
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from werkzeug.datastructures import FileStorage

from app.core.config import settings


class FileUtil:
    def __init__(self):
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
            region=settings.minio_region,
        )
        self._bucket = settings.minio_bucket
        self._root_prefix = settings.minio_root_prefix.strip("/")
        self._retries = max(1, getattr(settings, 'minio_upload_retries', 3))
        self._ensure_bucket()

    def upload_file(self, local_path: Path, relative_path: str) -> str:
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Artifact missing: {local_path}")
        object_name = self.object_name_for(relative_path)
        for attempt in range(1, self._retries + 1):
            try:
                self._client.fput_object(self._bucket, object_name, str(local_path))
                # 上传成功后删除本地文件
                try:
                    local_path.unlink()
                    logging.info(f"Deleted local file after upload: {local_path}")
                except Exception as exc:
                    logging.warning(f"Failed to delete local file {local_path}: {exc}")
                return self.get_url(object_name)
            except S3Error as exc:
                logging.error(
                    "MinIO upload failed (attempt %s/%s) for %s: %s",
                    attempt, self._retries, object_name, exc
                )
            except Exception as exc:
                logging.exception(
                    "Unexpected error during MinIO upload (attempt %s/%s) for %s",
                    attempt, self._retries, object_name
                )
            if attempt < self._retries:
                time.sleep(0.5 * (2 ** (attempt - 1)))
        raise RuntimeError(f"Failed to upload {local_path} to MinIO after {self._retries} attempts")

    def download_file(self, relative_path: str, local_path: Path) -> Path:
        object_name = self.object_name_for(relative_path)
        data = self._client.get_object(self._bucket, object_name)
        with open(local_path, 'wb') as f:
            for chunk in data.stream(32 * 1024):
                f.write(chunk)
        return local_path

    def delete_file(self, relative_path: str):
        object_name = self.object_name_for(relative_path)
        self._client.remove_object(self._bucket, object_name)

    def file_exists(self, relative_path: str) -> bool:
        object_name = self.object_name_for(relative_path)
        try:
            self._client.stat_object(self._bucket, object_name)
            return True
        except Exception:
            return False

    def get_url(self, object_name: str) -> str:
        scheme = "https" if settings.minio_secure else "http"
        endpoint = settings.minio_endpoint.rstrip("/")
        return f"{scheme}://{endpoint}/{self._bucket}/{object_name}"

    def object_name_for(self, relative_path: str) -> str:
        clean = Path(relative_path).as_posix().lstrip("/")
        if not clean or clean == "assets":
            raise ValueError("Object key must include file path under assets/")
        if not clean.startswith("assets/"):
            raise ValueError(f"Object key must start with assets/: {clean}")
        if self._root_prefix:
            return f"{self._root_prefix}/{clean}"
        return clean

    def _ensure_bucket(self):
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
        except Exception as exc:
            raise RuntimeError(f"Unable to access MinIO bucket '{self._bucket}'") from exc

    # 可选：读取OBJ内容
    def read_obj(self, relative_path: str) -> str:
        import tempfile
        object_name = self.object_name_for(relative_path)
        if not self.file_exists(relative_path):
            return None
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            self.download_file(relative_path, tmp.name)
            tmp.seek(0)
            content = tmp.read().decode('utf-8')
        Path(tmp.name).unlink()
        return content

    def upload_and_return_relative(self, local_path: Path, relative_path: str) -> str:
        """
        上传文件到 MinIO，但只返回 assets/ 开头的相对路径，不返回 MinIO URL。
        上传成功后删除本地文件。
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Artifact missing: {local_path}")
        object_name = self.object_name_for(relative_path)
        for attempt in range(1, self._retries + 1):
            try:
                self._client.fput_object(self._bucket, object_name, str(local_path))
                try:
                    local_path.unlink()
                    logging.info(f"Deleted local file after upload: {local_path}")
                except Exception as exc:
                    logging.warning(f"Failed to delete local file {local_path}: {exc}")
                return relative_path
            except S3Error as exc:
                logging.error(
                    "MinIO upload failed (attempt %s/%s) for %s: %s",
                    attempt, self._retries, object_name, exc
                )
            except Exception as exc:
                logging.exception(
                    "Unexpected error during MinIO upload (attempt %s/%s) for %s",
                    attempt, self._retries, object_name
                )
            if attempt < self._retries:
                time.sleep(0.5 * (2 ** (attempt - 1)))
        raise RuntimeError(f"Failed to upload {local_path} to MinIO after {self._retries} attempts")

#     上传直接现有文件目录下的所有内容以及子目录的嵌套内容到minio之中
def main(origin_str, target_str):
    """
    批量上传 origin_str 目录下所有文件（含子目录）到 MinIO，目标路径以 target_str 为根（建议 assets/ 开头）。
    自动补齐 assets/ 前缀，上传成功和失败均有日志输出。
    返回上传成功和失败的文件列表。
    """
    file_util = FileUtil()
    origin_path = Path(origin_str)
    if not origin_path.exists():
        raise FileNotFoundError(f"Origin path does not exist: {origin_path}")
    # 自动补齐 assets/ 前缀
    if not str(target_str).startswith("assets/"):
        target_str = f"assets/{target_str.lstrip('/')}"
    target_root = Path(target_str)
    success_files = []
    failed_files = []
    for root, dirs, files in os.walk(origin_path):
        for file in files:
            local_file = Path(root) / file
            relative_file = local_file.relative_to(origin_path)
            target_file = target_root / relative_file
            try:
                file_util.upload_file(local_file, str(target_file))
                logging.info(f"Uploaded: {local_file} -> {target_file}")
                success_files.append(str(target_file))
            except Exception as exc:
                logging.error(f"Failed to upload {local_file} -> {target_file}: {exc}")
                failed_files.append(str(target_file))
    logging.info(f"Upload finished. Success: {len(success_files)}, Failed: {len(failed_files)}")
    return success_files, failed_files

if __name__ == "__main__":
    str_1="D:\\CODE\\3d_city\\app\\assets"
    str_2="assets/"
    success_files, failed_files = main(str_1, str_2)
