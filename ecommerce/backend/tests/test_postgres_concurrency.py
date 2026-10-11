"""PostgreSQL concurrency evidence for the R-04 checkout risk."""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api import orders as orders_api
from app.api import payment as payment_api
from app.core.database import Base
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.security import get_current_admin
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User, UserAddress
from app.schemas.order import OrderCreate
from app.services.orders import OrderService


TEST_DATABASE_URL = os.getenv("POSTGRES_TEST_DATABASE_URL")

pytestmark = pytest.mark.postgres

if not TEST_DATABASE_URL:
    pytest.skip(
        "set POSTGRES_TEST_DATABASE_URL to run PostgreSQL integration evidence",
        allow_module_level=True,
    )


@dataclass(frozen=True)
class CheckoutFixture:
    user_id: UUID
    address_id: UUID
    product_id: UUID
    cart_item_id: UUID
    initial_sold_count: int


@pytest_asyncio.fixture(scope="module")
async def postgres_engine() -> AsyncEngine:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(postgres_engine: AsyncEngine):
    return async_sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def checkout_data(session_factory) -> CheckoutFixture:
    suffix = uuid4().hex
    user_id = uuid4()
    address_id = uuid4()
    product_id = uuid4()
    cart_item_id = uuid4()
    initial_sold_count = 11

    async with session_factory() as session:
        session.add_all([
            User(
                id=user_id,
                username=f"r04_{suffix}",
                email=f"r04_{suffix}@example.com",
                phone=f"13{suffix[:9]}",
                password_hash="not-used-in-this-test",
            ),
            UserAddress(
                id=address_id,
                user_id=user_id,
                recipient_name="R-04 Buyer",
                phone="13800138000",
                province="Shanghai",
                city="Shanghai",
                district="Pudong",
                address="R-04 Test Road",
            ),
            Product(
                id=product_id,
                name="R-04 last-unit product",
                slug=f"r04-{suffix}",
                price=Decimal("25.00"),
                stock=1,
                sold_count=initial_sold_count,
                is_active=True,
                specs={"evidence": "R-04"},
            ),
            CartItem(
                id=cart_item_id,
                user_id=user_id,
                product_id=product_id,
                quantity=1,
            ),
        ])
        await session.commit()

    return CheckoutFixture(
        user_id=user_id,
        address_id=address_id,
        product_id=product_id,
        cart_item_id=cart_item_id,
        initial_sold_count=initial_sold_count,
    )


@pytest.fixture
def checkout_app(session_factory):
    app = FastAPI()
    app.include_router(orders_api.router, prefix="/api")
    app.include_router(payment_api.router, prefix="/api")

    async def override_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def override_user():
        # The request fixture installs the matching user ID on the app.
        return SimpleNamespace(id=app.user_id)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_current_admin] = override_user
    app.user_id = None
    return app


def checkout_payload(data: CheckoutFixture, key: UUID, *, remark: str | None = None) -> dict:
    return {
        "address_id": str(data.address_id),
        "cart_item_ids": [str(data.cart_item_id)],
        "custom_items": [],
        "idempotency_key": str(key),
        "remark": remark,
    }


def install_two_request_gates(monkeypatch):
    """Make the two requests overlap at cart read and product locking."""
    cart_gate = asyncio.Barrier(2)
    product_gate = asyncio.Barrier(2)

    def gate_after(original, barrier):
        calls = 0
        calls_lock = asyncio.Lock()

        async def wrapped(self, *args, **kwargs):
            nonlocal calls
            result = await original(self, *args, **kwargs)
            async with calls_lock:
                calls += 1
                wait_for_gate = calls <= 2
            if wait_for_gate:
                await barrier.wait()
            return result

        return wrapped

    def gate_before(original, barrier):
        calls = 0
        calls_lock = asyncio.Lock()

        async def wrapped(self, *args, **kwargs):
            nonlocal calls
            async with calls_lock:
                calls += 1
                wait_for_gate = calls <= 2
            if wait_for_gate:
                await barrier.wait()
            return await original(self, *args, **kwargs)

        return wrapped

    monkeypatch.setattr(
        OrderService,
        "_get_cart_items",
        gate_after(OrderService._get_cart_items, cart_gate),
    )
    monkeypatch.setattr(
        OrderService,
        "_lock_products",
        gate_before(OrderService._lock_products, product_gate),
    )


async def read_inventory_state(session_factory, data: CheckoutFixture) -> tuple[int, int, int, int, int]:
    async with session_factory() as session:
        order_count = await session.scalar(
            select(func.count(Order.id)).where(Order.user_id == data.user_id)
        )
        item_count = await session.scalar(
            select(func.count(OrderItem.id)).join(Order).where(Order.user_id == data.user_id)
        )
        product = await session.scalar(select(Product).where(Product.id == data.product_id))
        cart_count = await session.scalar(
            select(func.count(CartItem.id)).where(CartItem.id == data.cart_item_id)
        )
        return int(order_count), int(item_count), product.stock, product.sold_count, int(cart_count)


@pytest.mark.asyncio
async def test_identical_keys_create_once_and_replay_after_last_unit_race(
    checkout_app,
    session_factory,
    checkout_data,
    monkeypatch,
):
    checkout_app.user_id = checkout_data.user_id
    install_two_request_gates(monkeypatch)
    key = uuid4()
    payload = checkout_payload(checkout_data, key)

    async with AsyncClient(
        transport=ASGITransport(app=checkout_app),
        base_url="http://test",
    ) as client:
        responses = await asyncio.gather(
            client.post("/api/orders", json=payload),
            client.post("/api/orders", json=payload),
        )

        assert [response.status_code for response in responses] == [201, 201]
        assert responses[0].json()["id"] == responses[1].json()["id"]
        assert responses[0].json()["order_no"] == responses[1].json()["order_no"]

        replay = await client.post("/api/orders", json=payload)
        assert replay.status_code == 201
        assert replay.json()["id"] == responses[0].json()["id"]

    order_count, item_count, stock, sold_count, cart_count = await read_inventory_state(
        session_factory,
        checkout_data,
    )
    assert (order_count, item_count, stock, sold_count, cart_count) == (
        1,
        1,
        0,
        checkout_data.initial_sold_count + 1,
        0,
    )


@pytest.mark.asyncio
async def test_distinct_keys_allow_only_one_last_unit_checkout(
    checkout_app,
    session_factory,
    checkout_data,
    monkeypatch,
):
    checkout_app.user_id = checkout_data.user_id
    install_two_request_gates(monkeypatch)
    payloads = [
        checkout_payload(checkout_data, uuid4()),
        checkout_payload(checkout_data, uuid4()),
    ]

    async with AsyncClient(
        transport=ASGITransport(app=checkout_app),
        base_url="http://test",
    ) as client:
        responses = await asyncio.gather(*[
            client.post("/api/orders", json=payload)
            for payload in payloads
        ])

    assert sorted(response.status_code for response in responses) == [201, 400]
    failed = next(response for response in responses if response.status_code == 400)
    assert "out of stock" in failed.json()["detail"]

    order_count, item_count, stock, sold_count, cart_count = await read_inventory_state(
        session_factory,
        checkout_data,
    )
    assert (order_count, item_count, stock, sold_count, cart_count) == (
        1,
        1,
        0,
        checkout_data.initial_sold_count + 1,
        0,
    )


@pytest.mark.asyncio
async def test_commit_failure_rolls_back_order_stock_sold_count_and_cart(
    session_factory,
    checkout_data,
    monkeypatch,
):
    key = uuid4()
    request = OrderCreate.model_validate(checkout_payload(checkout_data, key))

    async with session_factory() as session:
        async def fail_commit():
            raise RuntimeError("R-04 injected commit failure")

        monkeypatch.setattr(session, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="injected commit failure"):
            await OrderService(session).create_order(request, checkout_data.user_id)
        assert not session.in_transaction()

    order_count, item_count, stock, sold_count, cart_count = await read_inventory_state(
        session_factory,
        checkout_data,
    )
    assert (order_count, item_count, stock, sold_count, cart_count) == (
        0,
        0,
        1,
        checkout_data.initial_sold_count,
        1,
    )


@pytest.mark.asyncio
async def test_order_can_finish_payment_shipping_and_receipt_once(
    checkout_app, checkout_data, session_factory, monkeypatch,
):
    monkeypatch.setattr(payment_api.settings, "ALIPAY_SANDBOX", True)
    checkout_app.user_id = checkout_data.user_id
    async with AsyncClient(transport=ASGITransport(app=checkout_app), base_url="http://test") as client:
        created = await client.post("/api/orders", json=checkout_payload(checkout_data, uuid4()))
        assert created.status_code == 201, created.text
        order_id = created.json()["id"]

        premature = await client.post(f"/api/orders/{order_id}/complete")
        assert premature.status_code == 400
        paid = await client.post(f"/api/payment/sandbox/mock-pay/{order_id}")
        assert paid.status_code == 200, paid.text
        assert paid.json()["status"] == "paid"
        cancelled = await client.post(f"/api/orders/{order_id}/cancel", json={})
        assert cancelled.status_code == 400

        shipped = await client.post(f"/api/orders/{order_id}/ship", json={
            "shipping_company": "Local demo courier", "tracking_number": "DEMO-001",
        })
        assert shipped.status_code == 200, shipped.text
        assert shipped.json()["status"] == "shipped"

        checkout_app.user_id = uuid4()
        forbidden = await client.post(f"/api/orders/{order_id}/complete")
        assert forbidden.status_code == 404
        checkout_app.user_id = checkout_data.user_id
        completed = await client.post(f"/api/orders/{order_id}/complete")
        assert completed.status_code == 200, completed.text
        assert completed.json()["status"] == "completed"
        replay = await client.post(f"/api/orders/{order_id}/complete")
        assert replay.status_code == 200
        assert replay.json()["completed_at"] == completed.json()["completed_at"]

    state = await read_inventory_state(session_factory, checkout_data)
    assert state == (1, 1, 0, checkout_data.initial_sold_count + 1, 0)


@pytest.mark.asyncio
async def test_concurrent_cancellation_restores_inventory_only_once(
    checkout_app, checkout_data, session_factory,
):
    checkout_app.user_id = checkout_data.user_id
    async with AsyncClient(transport=ASGITransport(app=checkout_app), base_url="http://test") as client:
        created = await client.post("/api/orders", json=checkout_payload(checkout_data, uuid4()))
        assert created.status_code == 201, created.text
        order_id = created.json()["id"]
        results = await asyncio.gather(*[
            client.post(f"/api/orders/{order_id}/cancel", json={"reason": "Duplicate tap"})
            for _ in range(2)
        ])
        assert sorted(result.status_code for result in results) == [200, 400]

    state = await read_inventory_state(session_factory, checkout_data)
    assert state == (1, 1, 1, checkout_data.initial_sold_count, 0)
