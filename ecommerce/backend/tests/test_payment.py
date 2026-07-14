from uuid import UUID

from app.api.payment import AlipayService


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
