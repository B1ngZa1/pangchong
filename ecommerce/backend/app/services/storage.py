"""Server-only local/Supabase storage for catalog assets."""
import asyncio
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote

import httpx

from ..core.config import settings


class StorageNotConfigured(RuntimeError):
    pass


class StorageUploadError(RuntimeError):
    pass


@dataclass(frozen=True)
class StoredAsset:
    bucket: str
    path: str
    url: str
    mime_type: str
    size: int

    def to_dict(self) -> dict:
        return asdict(self)


class CatalogStorageService:
    """Stores assets locally by default or in Supabase when explicitly enabled."""

    @property
    def allowed_buckets(self) -> set[str]:
        return {settings.SUPABASE_IMAGE_BUCKET, settings.SUPABASE_MODEL_BUCKET}

    @property
    def is_configured(self) -> bool:
        if settings.ASSET_STORAGE_BACKEND == "local":
            return True
        return bool(settings.SUPABASE_URL and settings.SUPABASE_SECRET_KEY)

    async def upload(self, *, bucket: str, path: str, data: bytes, mime_type: str) -> StoredAsset:
        if bucket not in self.allowed_buckets:
            raise StorageUploadError("不允许写入该 Storage Bucket")
        if settings.ASSET_STORAGE_BACKEND == "local":
            return await self._upload_local(
                bucket=bucket,
                path=path,
                data=data,
                mime_type=mime_type,
            )
        if not self.is_configured:
            raise StorageNotConfigured("Supabase Storage 尚未配置")

        base_url = settings.SUPABASE_URL.rstrip("/")
        object_path = "/".join(quote(part, safe="") for part in path.split("/"))
        endpoint = f"{base_url}/storage/v1/object/{quote(bucket, safe='')}/{object_path}"
        headers = {
            "Authorization": f"Bearer {settings.SUPABASE_SECRET_KEY}",
            "apikey": settings.SUPABASE_SECRET_KEY,
            "Content-Type": mime_type,
            "x-upsert": "false",
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(endpoint, content=data, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:300]
            raise StorageUploadError(f"Storage 上传失败：{detail}") from exc
        except httpx.HTTPError as exc:
            raise StorageUploadError("无法连接 Supabase Storage") from exc

        public_url = f"{base_url}/storage/v1/object/public/{quote(bucket, safe='')}/{object_path}"
        return StoredAsset(
            bucket=bucket,
            path=path,
            url=public_url,
            mime_type=mime_type,
            size=len(data),
        )

    async def _upload_local(
        self,
        *,
        bucket: str,
        path: str,
        data: bytes,
        mime_type: str,
    ) -> StoredAsset:
        relative_path = PurePosixPath(path)
        if relative_path.is_absolute() or not relative_path.parts or ".." in relative_path.parts:
            raise StorageUploadError("本地存储路径无效")

        upload_root = Path(settings.UPLOAD_DIR).resolve()
        target = upload_root.joinpath(*relative_path.parts).resolve()
        try:
            target.relative_to(upload_root)
        except ValueError as exc:
            raise StorageUploadError("本地存储路径越界") from exc

        await asyncio.to_thread(target.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(target.write_bytes, data)
        public_path = "/".join(quote(part, safe="") for part in relative_path.parts)
        return StoredAsset(
            bucket=bucket,
            path=path,
            url=f"/uploads/{public_path}",
            mime_type=mime_type,
            size=len(data),
        )


storage_service = CatalogStorageService()
