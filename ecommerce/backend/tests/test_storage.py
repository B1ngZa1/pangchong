import json
import struct
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api.admin import _build_asset_usage_map, _has_valid_signature, _serialize_admin_product
from app.core.config import settings
from app.services.glb import DIY_MODEL_PART_KEYS, InvalidGlb, inspect_glb
from app.services.storage import (
    StorageAssetMissing,
    StorageNotConfigured,
    StorageUploadError,
    storage_service,
)


def make_glb(node_names):
    document = json.dumps(
        {
            "asset": {"version": "2.0"},
            "scene": 0,
            "scenes": [{"nodes": list(range(len(node_names)))}],
            "nodes": [{"name": name, "mesh": index} for index, name in enumerate(node_names)],
            "meshes": [{"primitives": []} for _ in node_names],
        },
        separators=(",", ":"),
    ).encode()
    document += b" " * ((4 - len(document) % 4) % 4)
    chunk = struct.pack("<II", len(document), 0x4E4F534A) + document
    return struct.pack("<4sII", b"glTF", 2, 12 + len(chunk)) + chunk


def test_glb_signature_requires_version_two():
    valid = b"glTF" + (2).to_bytes(4, "little") + (12).to_bytes(4, "little")
    invalid = b"glTF" + (1).to_bytes(4, "little") + (12).to_bytes(4, "little")
    assert _has_valid_signature(valid, ".glb") is True
    assert _has_valid_signature(invalid, ".glb") is False


def test_image_signatures_do_not_trust_extensions_only():
    assert _has_valid_signature(b"\x89PNG\r\n\x1a\ncontent", ".png") is True
    assert _has_valid_signature(b"not really a png", ".png") is False


def test_glb_contract_accepts_named_diy_nodes():
    report = inspect_glb(make_glb(DIY_MODEL_PART_KEYS))
    assert report.valid is True
    assert report.missing == ()


def test_glb_contract_reports_missing_nodes():
    report = inspect_glb(make_glb(["case", "mainboard", "cpu"]))
    assert report.found == ("case", "motherboard", "cpu")
    assert "gpu" in report.missing


def test_glb_contract_rejects_named_but_empty_part_groups():
    data = make_glb(DIY_MODEL_PART_KEYS)
    document_length = int.from_bytes(data[12:16], "little")
    document = json.loads(data[20:20 + document_length].decode().rstrip())
    document["nodes"][0].pop("mesh")
    payload = json.dumps(document, separators=(",", ":")).encode()
    payload += b" " * ((4 - len(payload) % 4) % 4)
    chunk = struct.pack("<II", len(payload), 0x4E4F534A) + payload
    report = inspect_glb(struct.pack("<4sII", b"glTF", 2, 12 + len(chunk)) + chunk)
    assert report.empty == ("case",)


def test_glb_parser_rejects_a_false_declared_length():
    data = bytearray(make_glb(DIY_MODEL_PART_KEYS))
    data[8:12] = (len(data) + 4).to_bytes(4, "little")
    try:
        inspect_glb(bytes(data))
    except InvalidGlb as exc:
        assert "长度" in str(exc)
    else:
        raise AssertionError("invalid GLB length was accepted")


def test_admin_product_payload_keeps_the_attached_model_metadata():
    product = SimpleNamespace(
        id=uuid4(),
        name="Defense Case",
        slug="defense-case",
        description=None,
        price=Decimal("999.00"),
        original_price=None,
        cost_price=None,
        category_id=uuid4(),
        brand="Demo",
        model="V1",
        stock=1,
        sold_count=0,
        image_url=None,
        images=[],
        specs={},
        model_3d_url="https://example.com/case.glb",
        model_3d_scale=Decimal("0.01"),
        model_3d_position=[0, 0.2, 0],
        model_3d_rotation=[0, 1.57, 0],
        asset_license="CC BY 4.0",
        asset_source_url="https://example.com/source",
        price_source_name="Catalog review",
        price_source_url="https://example.com/price",
        price_checked_at=datetime(2026, 9, 13, tzinfo=timezone.utc),
        weight=Decimal("8.2"),
        is_active=True,
        is_featured=True,
        created_at=datetime.now(timezone.utc),
    )

    payload = _serialize_admin_product(product)
    assert payload["model_3d_url"].endswith("/case.glb")
    assert payload["model_3d_scale"] == 0.01
    assert payload["asset_license"] == "CC BY 4.0"
    assert payload["asset_source_url"] == "https://example.com/source"
    assert payload["price_source_name"] == "Catalog review"
    assert payload["price_source_url"] == "https://example.com/price"
    assert payload["price_checked_at"] == "2026-09-13T00:00:00+00:00"


@pytest.mark.asyncio
async def test_local_storage_is_the_default_and_returns_a_public_path(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ASSET_STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))

    asset = await storage_service.upload(
        bucket=settings.SUPABASE_IMAGE_BUCKET,
        path="products/demo image.png",
        data=b"\x89PNG\r\n\x1a\ncontent",
        mime_type="image/png",
    )

    assert asset.url == "/uploads/products/demo%20image.png"
    assert (tmp_path / "products" / "demo image.png").read_bytes() == b"\x89PNG\r\n\x1a\ncontent"


@pytest.mark.asyncio
async def test_supabase_mode_requires_server_credentials(monkeypatch):
    monkeypatch.setattr(settings, "ASSET_STORAGE_BACKEND", "supabase")
    monkeypatch.setattr(settings, "SUPABASE_URL", "")
    monkeypatch.setattr(settings, "SUPABASE_SECRET_KEY", "")

    with pytest.raises(StorageNotConfigured):
        await storage_service.upload(
            bucket=settings.SUPABASE_IMAGE_BUCKET,
            path="products/demo.png",
            data=b"\x89PNG\r\n\x1a\ncontent",
            mime_type="image/png",
        )


def _use_local_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ASSET_STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))


@pytest.mark.asyncio
async def test_local_storage_lists_catalog_assets_and_ignores_other_files(tmp_path, monkeypatch):
    _use_local_storage(tmp_path, monkeypatch)
    (tmp_path / "products").mkdir()
    (tmp_path / "products" / "demo.png").write_bytes(b"\x89PNG\r\n\x1a\ncontent")
    (tmp_path / "products" / "sub").mkdir()
    (tmp_path / "products" / "sub" / "nested.webp").write_bytes(b"RIFFxxxxWEBP")
    (tmp_path / "products" / "notes.txt").write_text("ignore me")
    (tmp_path / "diy").mkdir()
    (tmp_path / "diy" / "case.glb").write_bytes(make_glb(DIY_MODEL_PART_KEYS))

    assets = await storage_service.list_assets()
    by_path = {asset.path: asset for asset in assets}

    assert set(by_path) == {"products/demo.png", "products/sub/nested.webp", "diy/case.glb"}
    assert by_path["products/demo.png"].kind == "image"
    assert by_path["products/demo.png"].mime_type == "image/png"
    assert by_path["products/demo.png"].bucket == settings.SUPABASE_IMAGE_BUCKET
    assert by_path["diy/case.glb"].kind == "model"
    assert by_path["diy/case.glb"].bucket == settings.SUPABASE_MODEL_BUCKET
    assert by_path["diy/case.glb"].updated_at is not None
    updated = [asset.updated_at for asset in assets]
    assert updated == sorted(updated, reverse=True)


@pytest.mark.asyncio
async def test_local_storage_list_on_missing_upload_dir_returns_empty(tmp_path, monkeypatch):
    _use_local_storage(tmp_path, monkeypatch)

    assert await storage_service.list_assets() == []


@pytest.mark.asyncio
async def test_local_storage_delete_removes_only_the_requested_asset(tmp_path, monkeypatch):
    _use_local_storage(tmp_path, monkeypatch)
    (tmp_path / "products").mkdir()
    (tmp_path / "products" / "demo.png").write_bytes(b"\x89PNG\r\n\x1a\ncontent")
    (tmp_path / "products" / "keep.png").write_bytes(b"\x89PNG\r\n\x1a\nkeep")

    await storage_service.delete_asset(bucket=settings.SUPABASE_IMAGE_BUCKET, path="products/demo.png")
    assert not (tmp_path / "products" / "demo.png").exists()
    assert (tmp_path / "products" / "keep.png").exists()

    with pytest.raises(StorageAssetMissing):
        await storage_service.delete_asset(bucket=settings.SUPABASE_IMAGE_BUCKET, path="products/demo.png")

    with pytest.raises(StorageUploadError):
        await storage_service.delete_asset(bucket=settings.SUPABASE_IMAGE_BUCKET, path="../escape.png")


class _StaticRows:
    def __init__(self, rows):
        self._rows = rows

    def __iter__(self):
        return iter(self._rows)


async def test_asset_usage_map_matches_local_and_remote_object_paths(mock_db):
    product_a = {"id": "id-a", "name": "机箱 A", "slug": "case-a"}
    product_b = {"id": "id-b", "name": "机箱 B", "slug": "case-b"}
    mock_db.execute.return_value = _StaticRows(
        [
            (
                product_a["id"],
                product_a["name"],
                product_a["slug"],
                "/uploads/products/a.png",
                ["/uploads/products/shared.webp"],
                None,
            ),
            (
                product_b["id"],
                product_b["name"],
                product_b["slug"],
                None,
                [],
                "https://supabase.example/storage/v1/object/public/catalog-models/diy/b.glb",
            ),
        ]
    )

    usage = await _build_asset_usage_map(mock_db, ["products/a.png", "diy/b.glb", "products/unused.png"])

    assert [product["id"] for product in usage["products/a.png"]] == ["id-a"]
    assert [product["id"] for product in usage["diy/b.glb"]] == ["id-b"]
    assert "products/unused.png" not in usage
