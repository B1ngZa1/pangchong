"""API regressions for server-owned DIY pricing and order snapshots."""
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api import orders as orders_api
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.services.diy_catalog import DIY_CONFIGURATION
from app.services.diy_compatibility import DIY_COMPATIBILITY_RULES_VERSION


USER_ID = UUID("10000000-0000-0000-0000-000000000001")
ADDRESS_ID = UUID("20000000-0000-0000-0000-000000000001")


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        if isinstance(self.value, list):
            return self.value[0] if self.value else None
        return self.value

    def scalar_one(self):
        value = self.scalar_one_or_none()
        if value is None:
            raise AssertionError("Expected one result")
        return value

    def scalars(self):
        return self

    def all(self):
        return self.value if isinstance(self.value, list) else [self.value]


class FakeOrderSession:
    """Small scripted session that still executes the production order service."""

    def __init__(self, products):
        self.products = products
        self.address = SimpleNamespace(
            recipient_name="Test Buyer",
            phone="13800138000",
            province="Guangdong",
            city="Shenzhen",
            district="Nanshan",
            address="1 Catalog Road",
        )
        # OrderService re-checks idempotency after loading the cart and again
        # after acquiring inventory locks.
        self.responses = [None, self.address, [], None, self.products, None]
        self.order = None
        self.order_items = []
        self.commits = 0
        self.rollbacks = 0

    async def execute(self, _statement):
        if not self.responses:
            raise AssertionError("Unexpected database query")
        response = self.responses.pop(0)
        if response == "saved_order":
            response = self.order
        return FakeResult(response)

    def add(self, instance):
        if isinstance(instance, Order):
            self.order = instance
        elif isinstance(instance, OrderItem):
            self.order_items.append(instance)

    async def flush(self):
        now = datetime.now(timezone.utc)
        self.order.created_at = self.order.created_at or now
        self.order.updated_at = self.order.updated_at or now
        self.order.items = list(self.order_items)

    async def commit(self):
        self.commits += 1

    async def rollback(self):
        self.rollbacks += 1

    async def delete(self, _instance):
        return None


def make_products():
    products = []
    specs_by_slot = {
        "cpu": {"socket": "AM5", "tdp": "65W"},
        "gpu": {"length": "300mm", "tdp": "100W"},
        "motherboard": {"socket": "AM5", "form_factor": "ATX", "memory": "DDR5 x4"},
        "ram": {"type": "DDR5"},
        "ssd": {},
        "cooler": {"type": "风冷单塔", "height": "155mm", "tdp_support": "150W"},
        "psu": {"wattage": "850W"},
        "case": {"mb_support": "ATX", "gpu_length": "400mm", "cooler_height": "175mm"},
    }
    for index, slot in enumerate(DIY_CONFIGURATION.slots.values(), start=1):
        products.append(Product(
            id=UUID(f"30000000-0000-0000-0000-{index:012d}"),
            name=f"Catalog {slot.id}",
            slug=f"catalog-{slot.id}",
            price=Decimal(f"{index * 100}.10"),
            category_id=slot.category_id,
            brand="Trusted",
            model=f"MODEL-{index}",
            stock=20,
            sold_count=0,
            image_url=f"/{slot.id}.png",
            specs={"catalog_revision": 7, "slot": slot.id, **specs_by_slot[slot.id]},
            is_active=True,
        ))
    return products


def configuration_payload(products, *, version=DIY_CONFIGURATION.version):
    products_by_category = {product.category_id: product for product in products}
    return {
        "configuration_id": DIY_CONFIGURATION.id,
        "version": version,
        "variant_id": "black",
        "material_id": "matte",
        "parts": [
            {
                "slot_id": slot.id,
                "product_id": str(products_by_category[slot.category_id].id),
                "quantity": 1,
            }
            for slot in DIY_CONFIGURATION.slots.values()
        ],
    }


@pytest.fixture
def api_harness():
    products = make_products()
    session = FakeOrderSession(products)
    app = FastAPI()
    app.include_router(orders_api.router, prefix="/api")

    async def override_db():
        yield session

    async def override_user():
        return SimpleNamespace(id=USER_ID)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    return app, session, products


def order_payload(products, **custom_item_overrides):
    custom_item = {
        "configuration": configuration_payload(products),
        "quantity": 1,
    }
    custom_item.update(custom_item_overrides)
    return {
        "address_id": str(ADDRESS_ID),
        "cart_item_ids": [],
        "custom_items": [custom_item],
    }


@pytest.mark.asyncio
async def test_api_rejects_forged_custom_price(api_harness):
    app, session, products = api_harness

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/orders", json=order_payload(products, price="0.01"))

    assert response.status_code == 422
    assert any(error["loc"][-1] == "price" for error in response.json()["detail"])
    assert session.order is None


@pytest.mark.asyncio
async def test_api_rejects_stale_diy_configuration_version(api_harness):
    app, session, products = api_harness
    payload = order_payload(products)
    payload["custom_items"][0]["configuration"]["version"] = DIY_CONFIGURATION.version + 1

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/orders", json=payload)

    assert response.status_code == 409
    assert "unsupported" in response.json()["detail"]
    assert session.order is None
    assert session.rollbacks == 1


@pytest.mark.asyncio
async def test_api_persists_server_priced_snapshot_after_catalog_changes(api_harness):
    app, session, products = api_harness
    session.responses.append("saved_order")
    expected_unit_price = sum((product.price for product in products), Decimal("0.00"))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/api/orders", json=order_payload(products))

        assert created.status_code == 201, created.text
        created_body = created.json()
        created_item = created_body["items"][0]
        created_snapshot = created_item["product_specs"]["_snapshot"]
        assert Decimal(created_body["total_amount"]) == expected_unit_price
        assert Decimal(created_item["price"]) == expected_unit_price
        assert created_item["configuration_id"] == DIY_CONFIGURATION.id
        assert created_item["configuration_version"] == DIY_CONFIGURATION.version
        assert created_snapshot["configuration_id"] == DIY_CONFIGURATION.id
        assert created_snapshot["version"] == DIY_CONFIGURATION.version
        assert Decimal(created_snapshot["pricing"]["total"]) == expected_unit_price
        assert [part["name"] for part in created_snapshot["parts"]] == [
            product.name for product in products
        ]

        for product in products:
            product.name = f"Changed {product.name}"
            product.price = Decimal("0.01")
            product.specs = {"catalog_revision": 8}

        session.responses.append("saved_order")
        fetched = await client.get(f"/api/orders/{created_body['id']}")

    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["items"][0] == created_item
    assert all(product.stock == 19 for product in products)


@pytest.mark.asyncio
async def test_api_persists_server_compatibility_checks_without_changing_frontend_snapshot_fields(api_harness):
    app, session, products = api_harness
    session.responses.append("saved_order")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/orders", json=order_payload(products))

    assert response.status_code == 201, response.text
    snapshot = response.json()["items"][0]["product_specs"]["_snapshot"]
    assert snapshot["version"] == DIY_CONFIGURATION.version
    assert snapshot["metrics"]["compatibility_status"] == "compatible"
    assert snapshot["metrics"]["compatibility_rules_version"] == DIY_COMPATIBILITY_RULES_VERSION
    assert all(check["level"] == "ok" for check in snapshot["metrics"]["compatibility"])
    assert {check["rule_id"] for check in snapshot["metrics"]["compatibility"]} == {
        "DIY-CPU-MOTHERBOARD-SOCKET",
        "DIY-RAM-MOTHERBOARD-TYPE",
        "DIY-MOTHERBOARD-CASE-FORM-FACTOR",
        "DIY-GPU-CASE-LENGTH",
        "DIY-COOLER-CASE-HEIGHT",
        "DIY-PSU-HEADROOM",
    }


@pytest.mark.asyncio
async def test_api_blocks_incompatible_diy_socket_with_rule_id_and_remediation(api_harness):
    app, session, products = api_harness
    by_slot = {slot.id: products[index] for index, slot in enumerate(DIY_CONFIGURATION.slots.values())}
    by_slot["motherboard"].specs["socket"] = "LGA1700"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/orders", json=order_payload(products))

    assert response.status_code == 409
    body = response.json()
    issue = next(item for item in body["compatibility"]["issues"] if item["rule_id"] == "DIY-CPU-MOTHERBOARD-SOCKET")
    assert body["compatibility"]["status"] == "incompatible"
    assert issue["status"] == "incompatible"
    assert issue["remediation"]
    assert issue["rule_id"] in body["detail"]
    assert issue["remediation"] in body["detail"]
    assert session.order is None
    assert session.commits == 0
    assert session.rollbacks == 1


@pytest.mark.asyncio
async def test_api_blocks_unverified_diy_critical_rule(api_harness):
    app, session, products = api_harness
    by_slot = {slot.id: products[index] for index, slot in enumerate(DIY_CONFIGURATION.slots.values())}
    del by_slot["case"].specs["gpu_length"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/orders", json=order_payload(products))

    assert response.status_code == 409
    body = response.json()
    issue = next(item for item in body["compatibility"]["issues"] if item["rule_id"] == "DIY-GPU-CASE-LENGTH")
    assert body["compatibility"]["status"] == "unverified"
    assert issue["status"] == "unverified"
    assert "verified" in issue["remediation"]
    assert session.order is None
    assert session.commits == 0
    assert session.rollbacks == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("slot_id", "spec_key", "value", "rule_id"),
    [
        ("ram", "type", "DDR4", "DIY-RAM-MOTHERBOARD-TYPE"),
        ("motherboard", "form_factor", "E-ATX", "DIY-MOTHERBOARD-CASE-FORM-FACTOR"),
        ("gpu", "length", "500mm", "DIY-GPU-CASE-LENGTH"),
        ("cooler", "height", "200mm", "DIY-COOLER-CASE-HEIGHT"),
        ("psu", "wattage", "200W", "DIY-PSU-HEADROOM"),
    ],
)
async def test_api_blocks_each_incompatible_diy_rule(api_harness, slot_id, spec_key, value, rule_id):
    app, session, products = api_harness
    by_slot = {slot.id: products[index] for index, slot in enumerate(DIY_CONFIGURATION.slots.values())}
    by_slot[slot_id].specs[spec_key] = value

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/orders", json=order_payload(products))

    assert response.status_code == 409
    body = response.json()
    issue = next(item for item in body["compatibility"]["issues"] if item["rule_id"] == rule_id)
    assert body["compatibility"]["status"] == "incompatible"
    assert issue["status"] == "incompatible"
    assert issue["remediation"]
    assert session.order is None
    assert session.commits == 0
    assert session.rollbacks == 1
