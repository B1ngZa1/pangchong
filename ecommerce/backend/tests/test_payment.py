from decimal import Decimal
from uuid import UUID, uuid4
from urllib.parse import parse_qs, urlsplit

import pytest
from httpx import ASGITransport, AsyncClient
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.api.payment import AlipayService
from app.integrations.payments.alipay import AlipayPaymentAdapter
from app.models.order import Order
from app.models.payment_event import PaymentEvent
from app.services.payment import PaymentCallbackError, PaymentService


def make_adapter():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return AlipayPaymentAdapter(
        app_id="2026000000000001",
        private_key=private_pem,
        public_key=public_pem,
        sandbox=True,
    )


def signed_callback(adapter, **overrides):
    params = {
        "app_id": adapter.app_id,
        "notify_id": "notify-001",
        "out_trade_no": "PC-TEST-001",
        "trade_no": "trade-001",
        "trade_status": "TRADE_SUCCESS",
        "total_amount": "99.00",
        "sign_type": "RSA2",
    }
    params.update(overrides)
    params["sign"] = adapter.sign_params(params)
    return params


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class NestedTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class MemoryPaymentDb:
    """Small async-session double that preserves event durability semantics."""

    def __init__(self, order):
        self.order = order
        self.events = []
        self.pending = []

    async def execute(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        if entity is Order:
            return FakeResult(self.order)

        compiled = statement.compile()
        params = compiled.params
        field = "event_key" if "event_key_1" in params else "dedupe_key"
        value = params.get(f"{field}_1")
        return FakeResult(next((event for event in self.events if getattr(event, field) == value), None))

    def begin_nested(self):
        return NestedTransaction()

    def add(self, value):
        self.pending.append(value)

    async def flush(self):
        self.events.extend(self.pending)
        self.pending.clear()


def test_sandbox_callback_still_requires_rsa2_and_configured_app_id():
    adapter = make_adapter()
    callback = signed_callback(adapter)

    assert adapter.verify_callback(callback)

    forged = dict(callback, total_amount="0.01")
    assert not adapter.verify_callback(forged)
    assert not adapter.verify_callback(dict(callback, app_id="attacker-app"))
    assert not adapter.verify_callback(dict(callback, sign_type="RSA"))


@pytest.mark.asyncio
async def test_duplicate_and_out_of_order_notifications_are_durable_and_monotonic():
    adapter = make_adapter()
    order = Order(
        id=uuid4(),
        order_no="PC-TEST-001",
        status="pending",
        final_amount=Decimal("99.00"),
        payment_method="alipay",
    )
    db = MemoryPaymentDb(order)
    service = PaymentService(adapter)

    success = signed_callback(adapter)
    await service.handle_alipay_callback(db, success)
    await service.handle_alipay_callback(db, success)
    await service.handle_alipay_callback(
        db,
        signed_callback(adapter, notify_id="notify-duplicate"),
    )

    # A later closed notification is recorded but cannot regress a paid order.
    closed = signed_callback(
        adapter,
        notify_id="notify-002",
        trade_status="TRADE_CLOSED",
    )
    await service.handle_alipay_callback(db, closed)

    assert order.status == "paid"
    assert order.payment_id == "trade-001"
    assert len(db.events) == 2
    assert {event.processing_result for event in db.events} == {"paid", "ignored"}


@pytest.mark.asyncio
async def test_server_owned_amount_is_checked_with_decimal():
    adapter = make_adapter()
    order = Order(
        id=uuid4(),
        order_no="PC-TEST-001",
        status="pending",
        final_amount=Decimal("99.00"),
        payment_method="alipay",
    )
    db = MemoryPaymentDb(order)
    service = PaymentService(adapter)
    mismatched = signed_callback(adapter, total_amount="98.99")

    with pytest.raises(PaymentCallbackError, match="金额不匹配"):
        await service.handle_alipay_callback(db, mismatched)
    assert order.status == "pending"
    assert db.events == []


@pytest.mark.asyncio
async def test_callback_cannot_pay_order_without_alipay_handoff():
    adapter = make_adapter()
    order = Order(
        id=uuid4(),
        order_no="PC-TEST-001",
        status="pending",
        final_amount=Decimal("99.00"),
        payment_method=None,
    )
    db = MemoryPaymentDb(order)
    service = PaymentService(adapter)

    with pytest.raises(PaymentCallbackError, match="支付方式不匹配"):
        await service.handle_alipay_callback(db, signed_callback(adapter))

    assert order.status == "pending"
    assert db.events == []


@pytest.mark.asyncio
async def test_valid_callback_returns_plain_text_success(monkeypatch):
    import importlib

    payment_api = importlib.import_module("app.api.payment")
    from app.core.database import get_db
    from app.main import app

    adapter = make_adapter()
    order = Order(
        id=uuid4(),
        order_no="PC-TEST-001",
        status="pending",
        final_amount=Decimal("99.00"),
        payment_method="alipay",
    )
    db = MemoryPaymentDb(order)
    monkeypatch.setattr(payment_api, "payment_service", PaymentService(adapter))

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.post(
                "/api/payment/callback/alipay",
                data=signed_callback(adapter),
            )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.text == "success"
    assert response.headers["content-type"].startswith("text/plain")


def test_sandbox_payment_stays_on_the_local_order_route():
    service = AlipayService()
    service.sandbox = True

    url = service.create_payment_url(
        order_no="PC-DEMO",
        amount=99.0,
        subject="Demo order",
        order_id=UUID("c0000000-0000-0000-0000-000000000002"),
    )

    assert url == "/sandbox/orders/c0000000-0000-0000-0000-000000000002"


def test_production_payment_url_is_rsa2_signed_and_contains_server_amount():
    adapter = make_adapter()
    adapter.sandbox = False
    adapter.gateway = "https://gateway.example.test/gateway.do"

    url = adapter.create_payment_url(
        order_no="PC-TEST-001",
        amount=Decimal("99.00"),
        subject="Demo order",
    )
    params = {key: values[0] for key, values in parse_qs(urlsplit(url).query).items()}

    assert url.startswith("https://gateway.example.test/gateway.do?")
    assert params["sign_type"] == "RSA2"
    assert adapter.verify_callback(params)
    assert '"total_amount":"99.00"' in params["biz_content"]
