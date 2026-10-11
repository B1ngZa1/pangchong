"""Payment API routes."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import settings
from ..core.database import get_db
from ..core.security import get_current_user
from ..integrations.payments.alipay import AlipayPaymentAdapter
from ..models.order import Order, OrderItem
from ..models.user import User
from ..schemas.order import OrderPayRequest, OrderResponse
from ..services.payment import PaymentCallbackError, PaymentService

router = APIRouter(prefix="/payment", tags=["支付"])


# Kept as the public name used by existing callers/tests while the provider
# implementation lives in an integration adapter.
AlipayService = AlipayPaymentAdapter
alipay_service = AlipayService()
payment_service = PaymentService(alipay_service)


@router.post("/create/{order_id}")
async def create_payment(
    order_id: UUID,
    pay_data: OrderPayRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a payment handoff using the server-owned order amount."""
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id).with_for_update()
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单状态不允许支付")

    order.payment_method = pay_data.payment_method
    await db.flush()

    if pay_data.payment_method == "alipay":
        items_result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
        items = items_result.scalars().all()
        subject = f"胖虫科技-{items[0].product_name}" if items else "胖虫科技订单"
        try:
            payment_url = alipay_service.create_payment_url(
                order_no=order.order_no,
                amount=Decimal(str(order.final_amount)),
                subject=subject,
                order_id=order.id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        return {
            "payment_url": payment_url,
            "order_no": order.order_no,
            "amount": Decimal(str(order.final_amount)),
        }

    if pay_data.payment_method == "wechat":
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="微信支付暂未实现")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的支付方式")


@router.post("/callback/alipay", response_class=PlainTextResponse)
async def alipay_callback(request: Request, db: AsyncSession = Depends(get_db)) -> PlainTextResponse:
    """Receive a verified Alipay notification without requiring user login."""
    form_data = await request.form()
    # Never persist or log the raw form.  The adapter retains only identifiers
    # and a digest after RSA2 verification.
    params = {str(key): str(value) for key, value in form_data.items()}
    try:
        await payment_service.handle_alipay_callback(db, params)
    except PaymentCallbackError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return PlainTextResponse("success")


@router.post("/sandbox/mock-pay/{order_id}", response_model=OrderResponse)
async def sandbox_mock_pay(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Demo-only direct payment; real callbacks still require RSA2 in sandbox."""
    if not settings.ALIPAY_SANDBOX:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.user_id == current_user.id)
        .with_for_update()
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单状态不允许支付")

    order.status = "paid"
    order.payment_id = f"MOCK_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    order.paid_at = datetime.now(timezone.utc)
    await db.flush()
    return order


@router.get("/status/{order_no}")
async def get_payment_status(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query payment status for the current user's order."""
    result = await db.execute(
        select(Order).where(Order.order_no == order_no, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return {
        "order_no": order.order_no,
        "status": order.status,
        "is_paid": order.is_paid,
        "paid_at": order.paid_at,
        "payment_id": order.payment_id,
    }
