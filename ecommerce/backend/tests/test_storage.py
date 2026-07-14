import json
import struct
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api.admin import _has_valid_signature, _serialize_admin_product
from app.core.config import settings
from app.services.glb import DIY_MODEL_PART_KEYS, InvalidGlb, inspect_glb
from app.services.storage import StorageNotConfigured, storage_service


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
