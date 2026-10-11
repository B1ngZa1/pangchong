"""Payment application service: validation, state transitions, and idempotency."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..integrations.payments.alipay import AlipayCallbackError, AlipayPaymentAdapter
from ..models.order import Order
from ..models.payment_event import PaymentEvent


class PaymentCallbackError(Exception):
    """Safe, user-facing callback rejection with an HTTP status."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def _server_amount(value: object) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise PaymentCallbackError(500, "订单金额无效") from exc
    if not amount.is_finite():
        raise PaymentCallbackError(500, "订单金额无效")
    return amount.quantize(Decimal("0.01"))


class PaymentService:
    """Apply verified Alipay notifications in the same transaction as orders."""

    def __init__(self, alipay: AlipayPaymentAdapter) -> None:
        self.alipay = alipay

    async def handle_alipay_callback(
        self,
        db: AsyncSession,
        params: dict[str, object],
    ) -> None:
        try:
            callback = self.alipay.parse_callback(params)
        except AlipayCallbackError as exc:
            # Adapter errors contain only fixed validation messages, never key
            # material or the raw callback body.
            raise PaymentCallbackError(400, str(exc)) from exc

        order_result = await db.execute(
            select(Order)
            .where(Order.order_no == callback.order_no)
            .with_for_update()
        )
        order = order_result.scalar_one_or_none()
        if order is None:
            raise PaymentCallbackError(404, "订单不存在")

        # A provider notification must only settle an order that explicitly
        # started an Alipay payment handoff.  Accepting ``None`` here would
        # let a validly signed callback mark any pending order as paid before
        # the user selected a payment method (or after an incomplete checkout).
        if order.payment_method != "alipay":
            raise PaymentCallbackError(400, "支付方式不匹配")

        # Compare Decimal values derived from the persisted order snapshot.  A
        # client/provider amount can never override the server-owned amount.
        if callback.amount != _server_amount(order.final_amount):
            raise PaymentCallbackError(400, "金额不匹配")

        existing = await self._find_event(db, "event_key", callback.event_key)
        if existing is not None:
            self._ensure_same_event(existing, callback, require_payload_hash=True)
            return

        existing = await self._find_event(db, "dedupe_key", callback.dedupe_key)
        if existing is not None:
            self._ensure_same_event(existing, callback, require_payload_hash=False)
            return

        event = PaymentEvent(
            provider="alipay",
            event_key=callback.event_key,
            dedupe_key=callback.dedupe_key,
            order_id=order.id,
            order_no=order.order_no,
            trade_no=callback.trade_no,
            notification_id=callback.notification_id,
            trade_status=callback.trade_status,
            amount=callback.amount,
            payload_hash=callback.payload_hash,
            processing_result="ignored",
            received_at=callback.received_at,
        )

        try:
            # The order row lock serializes different valid notifications for
            # this order.  The savepoint also handles a duplicate arriving
            # between the two existence checks without aborting the request's
            # outer transaction.
            async with db.begin_nested():
                db.add(event)
                await db.flush()
        except IntegrityError:
            existing = await self._find_event(db, "dedupe_key", callback.dedupe_key)
            if existing is not None:
                self._ensure_same_event(existing, callback, require_payload_hash=False)
                return
            raise

        if callback.trade_status in {"TRADE_SUCCESS", "TRADE_FINISHED"}:
            if order.status not in {"pending", "paid", "shipped", "completed"}:
                raise PaymentCallbackError(409, "订单状态不允许支付")
            if order.payment_id and order.payment_id != callback.trade_no:
                raise PaymentCallbackError(409, "交易流水号不匹配")
            if not order.is_paid:
                order.status = "paid"
                order.payment_id = callback.trade_no
                order.paid_at = datetime.now(timezone.utc)
                event.processing_result = "paid"
                event.applied_at = datetime.now(timezone.utc)
            else:
                # A later success/finished notification for the same trade is
                # valid, durable, and intentionally has no second side effect.
                if not order.payment_id:
                    order.payment_id = callback.trade_no
                event.processing_result = "already_paid"
                event.applied_at = datetime.now(timezone.utc)
        else:
            # WAIT_BUYER_PAY and TRADE_CLOSED are audit events.  They must not
            # regress a paid order, and a later success notification may still
            # advance a pending order.
            event.processing_result = "ignored"
            event.applied_at = datetime.now(timezone.utc)

        await db.flush()

    @staticmethod
    async def _find_event(db: AsyncSession, field: str, value: str) -> PaymentEvent | None:
        column = getattr(PaymentEvent, field)
        result = await db.execute(
            select(PaymentEvent).where(
                PaymentEvent.provider == "alipay",
                column == value,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _ensure_same_event(existing: PaymentEvent, callback, *, require_payload_hash: bool) -> None:
        # Same provider key with a different payload is not a retry; it is a
        # tampered/reused notification identity and must not be acknowledged.
        same_business_event = (
            existing.order_no == callback.order_no
            and existing.trade_no == callback.trade_no
            and existing.trade_status == callback.trade_status
            and Decimal(str(existing.amount)) == callback.amount
        )
        if not same_business_event or (require_payload_hash and existing.payload_hash != callback.payload_hash):
            raise PaymentCallbackError(400, "支付事件不匹配")


__all__ = ["PaymentCallbackError", "PaymentService"]
