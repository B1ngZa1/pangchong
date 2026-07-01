"""Server-only Supabase Storage client for catalog assets."""
from dataclasses import asdict, dataclass
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


class SupabaseStorageService:
    """Uploads with a backend-only secret key; public clients receive URLs only."""

    @property
    def allowed_buckets(self) -> set[str]:
        return {settings.SUPABASE_IMAGE_BUCKET, settings.SUPABASE_MODEL_BUCKET}

    @property
    def is_configured(self) -> bool:
        return bool(settings.SUPABASE_URL and settings.SUPABASE_SECRET_KEY)

    async def upload(self, *, bucket: str, path: str, data: bytes, mime_type: str) -> StoredAsset:
        if not self.is_configured:
            raise StorageNotConfigured("Supabase Storage 尚未配置")
        if bucket not in self.allowed_buckets:
            raise StorageUploadError("不允许写入该 Storage Bucket")

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


storage_service = SupabaseStorageService()
