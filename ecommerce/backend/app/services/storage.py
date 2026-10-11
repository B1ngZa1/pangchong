"""Server-only local/Supabase storage for catalog assets."""
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Optional
from urllib.parse import quote

import httpx

from ..core.config import settings


class StorageNotConfigured(RuntimeError):
    pass


class StorageUploadError(RuntimeError):
    pass


class StorageAssetMissing(RuntimeError):
    pass


CATALOG_ASSET_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".glb": "model/gltf-binary",
}

LOCAL_MODEL_FOLDER = "diy"


@dataclass(frozen=True)
class StoredAsset:
    bucket: str
    path: str
    url: str
    mime_type: str
    size: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class StoredAssetInfo:
    bucket: str
    path: str
    url: str
    mime_type: str
    size: int
    kind: str  # "image" | "model"
    updated_at: Optional[str] = None

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

    async def list_assets(self) -> list[StoredAssetInfo]:
        """List catalog assets of both buckets, newest first."""
        if settings.ASSET_STORAGE_BACKEND == "local":
            return await asyncio.to_thread(self._scan_local)
        if not self.is_configured:
            raise StorageNotConfigured("Supabase Storage 尚未配置")
        return await self._list_supabase()

    async def delete_asset(self, *, bucket: str, path: str) -> None:
        if bucket not in self.allowed_buckets:
            raise StorageUploadError("不允许删除该 Storage Bucket 对象")
        if settings.ASSET_STORAGE_BACKEND == "local":
            await self._delete_local(path=path)
            return
        if not self.is_configured:
            raise StorageNotConfigured("Supabase Storage 尚未配置")
        await self._delete_supabase(bucket=bucket, path=path)

    def _scan_local(self) -> list[StoredAssetInfo]:
        upload_root = Path(settings.UPLOAD_DIR).resolve()
        if not upload_root.exists():
            return []

        assets: list[StoredAssetInfo] = []
        for file_path in upload_root.rglob("*"):
            if not file_path.is_file():
                continue
            mime_type = CATALOG_ASSET_MIME.get(file_path.suffix.lower())
            if not mime_type:
                continue
            relative = file_path.relative_to(upload_root)
            path = "/".join(relative.parts)
            kind = "model" if relative.parts[0] == LOCAL_MODEL_FOLDER else "image"
            bucket = (
                settings.SUPABASE_MODEL_BUCKET if kind == "model" else settings.SUPABASE_IMAGE_BUCKET
            )
            stat = file_path.stat()
            assets.append(
                StoredAssetInfo(
                    bucket=bucket,
                    path=path,
                    url=f"/uploads/{path}",
                    mime_type=mime_type,
                    size=stat.st_size,
                    kind=kind,
                    updated_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                )
            )
        assets.sort(key=lambda asset: asset.updated_at or "", reverse=True)
        return assets

    async def _list_supabase(self) -> list[StoredAssetInfo]:
        base_url = settings.SUPABASE_URL.rstrip("/")
        headers = {
            "Authorization": f"Bearer {settings.SUPABASE_SECRET_KEY}",
            "apikey": settings.SUPABASE_SECRET_KEY,
        }
        assets: list[StoredAssetInfo] = []
        async with httpx.AsyncClient(timeout=30) as client:
            for bucket, kind in (
                (settings.SUPABASE_IMAGE_BUCKET, "image"),
                (settings.SUPABASE_MODEL_BUCKET, "model"),
            ):
                endpoint = f"{base_url}/storage/v1/object/list/{quote(bucket, safe='')}"
                payload = {
                    "prefix": "",
                    "limit": 1000,
                    "offset": 0,
                    "sortBy": {"column": "created_at", "order": "desc"},
                }
                try:
                    response = await client.post(endpoint, json=payload, headers=headers)
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    detail = exc.response.text[:300]
                    raise StorageUploadError(f"Storage 素材列表读取失败：{detail}") from exc
                except httpx.HTTPError as exc:
                    raise StorageUploadError("无法连接 Supabase Storage") from exc

                for item in response.json():
                    metadata = item.get("metadata") or {}
                    name = item.get("name") or ""
                    if not metadata or not name:
                        continue  # 目录占位条目
                    suffix = Path(name).suffix.lower()
                    object_path = "/".join(quote(part, safe="") for part in name.split("/"))
                    assets.append(
                        StoredAssetInfo(
                            bucket=bucket,
                            path=name,
                            url=f"{base_url}/storage/v1/object/public/{quote(bucket, safe='')}/{object_path}",
                            mime_type=metadata.get("mimetype") or CATALOG_ASSET_MIME.get(suffix, "application/octet-stream"),
                            size=int(metadata.get("size") or 0),
                            kind=kind,
                            updated_at=item.get("updated_at") or item.get("created_at"),
                        )
                    )
        return assets

    async def _delete_local(self, *, path: str) -> None:
        relative_path = PurePosixPath(path)
        if relative_path.is_absolute() or not relative_path.parts or ".." in relative_path.parts:
            raise StorageUploadError("本地存储路径无效")

        upload_root = Path(settings.UPLOAD_DIR).resolve()
        target = upload_root.joinpath(*relative_path.parts).resolve()
        try:
            target.relative_to(upload_root)
        except ValueError as exc:
            raise StorageUploadError("本地存储路径越界") from exc

        if not target.is_file():
            raise StorageAssetMissing("素材文件不存在")
        await asyncio.to_thread(target.unlink)

    async def _delete_supabase(self, *, bucket: str, path: str) -> None:
        base_url = settings.SUPABASE_URL.rstrip("/")
        object_path = "/".join(quote(part, safe="") for part in path.split("/"))
        endpoint = f"{base_url}/storage/v1/object/{quote(bucket, safe='')}/{object_path}"
        headers = {
            "Authorization": f"Bearer {settings.SUPABASE_SECRET_KEY}",
            "apikey": settings.SUPABASE_SECRET_KEY,
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.delete(endpoint, headers=headers)
                if response.status_code == 404:
                    raise StorageAssetMissing("素材在 Storage 中不存在")
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:300]
            raise StorageUploadError(f"Storage 删除失败：{detail}") from exc
        except httpx.HTTPError as exc:
            raise StorageUploadError("无法连接 Supabase Storage") from exc


storage_service = CatalogStorageService()
