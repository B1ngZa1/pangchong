"""Integration tests for the admin asset library endpoints."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.security import get_current_admin
from app.main import app

from test_storage import _StaticRows, make_glb


@pytest.fixture
def admin_client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.ASSET_STORAGE_BACKEND", "local")
    monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(tmp_path))
    (tmp_path / "products").mkdir()
    (tmp_path / "products" / "used.png").write_bytes(b"\x89PNG\r\n\x1a\nused")
    (tmp_path / "products" / "orphan.png").write_bytes(b"\x89PNG\r\n\x1a\norphan")
    (tmp_path / "diy").mkdir()
    (tmp_path / "diy" / "case.glb").write_bytes(make_glb(["case", "motherboard", "cpu", "gpu", "ram", "ssd", "cooler", "psu"]))

    session = MagicMock()
    session.execute = AsyncMock(
        return_value=_StaticRows(
            [
                ("pid-1", "已引用商品", "used-product", "/uploads/products/used.png", [], None),
            ]
        )
    )
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_admin] = lambda: SimpleNamespace(id="admin-id")
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_admin, None)


def test_admin_assets_endpoint_lists_summary_and_usage(admin_client):
    response = admin_client.get("/api/admin/assets")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["total"] == 3
    assert body["summary"]["images"] == 2
    assert body["summary"]["models"] == 1
    assert body["summary"]["unused"] == 2
    assert body["summary"]["total_size"] == sum(item["size"] for item in body["items"])

    by_path = {item["path"]: item for item in body["items"]}
    assert by_path["products/used.png"]["used_by"] == [
        {"id": "pid-1", "name": "已引用商品", "slug": "used-product"}
    ]
    assert by_path["products/orphan.png"]["used_by"] == []
    assert by_path["diy/case.glb"]["kind"] == "model"
    assert by_path["products/used.png"]["url"] == "/uploads/products/used.png"


def test_admin_assets_endpoint_filters_by_kind(admin_client):
    response = admin_client.get("/api/admin/assets", params={"kind": "model"})

    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["path"] for item in items] == ["diy/case.glb"]


def test_admin_assets_delete_blocks_referenced_asset(admin_client):
    response = admin_client.delete("/api/admin/assets/products/used.png")

    assert response.status_code == 409
    assert "已引用商品" in response.json()["detail"]


def test_admin_assets_delete_removes_orphan_asset(admin_client):
    response = admin_client.delete("/api/admin/assets/products/orphan.png")

    assert response.status_code == 204


def test_admin_assets_delete_reports_missing_asset(admin_client):
    response = admin_client.delete("/api/admin/assets/products/ghost.png")

    assert response.status_code == 404


def test_admin_model_upload_keeps_the_model_contract_form_field(admin_client):
    response = admin_client.post(
        "/api/admin/assets",
        data={"model_contract": "diy-case-v1"},
        files={
            "file": (
                "case.glb",
                make_glb(["case", "motherboard", "cpu", "gpu", "ram", "ssd", "cooler", "psu"]),
                "model/gltf-binary",
            )
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["path"].startswith("diy/")
    assert body["node_contract"]["valid"] is True
