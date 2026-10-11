"""
胖虫电商系统 - 订单 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from ..core.database import get_db
from ..core.security import get_current_user, get_current_admin
from ..models.user import User
from ..models.product import Product
from ..models.order import Order
from ..schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderPayRequest,
    OrderShipRequest,
    OrderCancelRequest,
)
from ..services.orders import OrderCreationError, OrderService, inventory_from_order_items

router = APIRouter(prefix="/orders", tags=["订单"])


# ============ 创建订单 ============

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    从购物车创建订单

    - **address_id**: 收货地址ID
    - **remark**: 订单备注（可选）
    - **cart_item_ids**: 购物车商品ID列表（可选，为空则结算全部）
    """
    try:
        return await OrderService(db).create_order(order_data, current_user.id)
    except OrderCreationError as exc:
        if exc.payload is not None:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, **exc.payload},
            )
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


# ============ 获取订单列表 ============

@router.get("", response_model=OrderListResponse)
async def get_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="订单状态"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的订单列表"""
    query = select(Order).where(Order.user_id == current_user.id)

    # 状态筛选
    if status:
        query = query.where(Order.status == status)

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页查询
    query = query.options(selectinload(Order.items))
    query = query.order_by(Order.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    orders = result.scalars().all()

    return OrderListResponse(
        items=orders,
        total=total,
        page=page,
        page_size=page_size
    )


# ============ 获取订单详情 ============

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    return order


# ============ 取消订单 ============

@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID,
    cancel_data: OrderCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消订单（仅待支付状态可取消）"""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
        .with_for_update()
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if not order.can_cancel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前订单状态不可取消"
        )

    # Restore stock from normal-product and server-built DIY snapshots.
    inventory = inventory_from_order_items(order.items)
    for product_id in sorted(inventory, key=str):
        quantity = inventory[product_id]
        result = await db.execute(select(Product).where(Product.id == product_id).with_for_update())
        product = result.scalar_one_or_none()
        if product:
            product.stock += quantity
            product.sold_count = max(0, (product.sold_count or 0) - quantity)

    # 更新订单状态
    order.status = "cancelled"
    order.remark = f"{order.remark or ''}\n取消原因：{cancel_data.reason or '用户主动取消'}"

    await db.flush()
    return order


@router.post("/{order_id}/complete", response_model=OrderResponse)
async def complete_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Let the recipient confirm delivery; repeated confirmations are safe."""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.user_id == current_user.id)
        .with_for_update()
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status == "completed":
        return order
    if order.status != "shipped":
        raise HTTPException(status_code=400, detail="只有已发货的订单才能确认收货")
    order.status = "completed"
    order.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return order


# ============ 管理员：订单发货 ============

@router.post("/{order_id}/ship", response_model=OrderResponse)
async def ship_order(
    order_id: UUID,
    ship_data: OrderShipRequest,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """订单发货（管理员）"""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
        .with_for_update()
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.status != "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有已支付的订单才能发货"
        )

    order.status = "shipped"
    order.shipping_company = ship_data.shipping_company
    order.tracking_number = ship_data.tracking_number
    order.shipped_at = datetime.utcnow()

    await db.flush()
    return order


# ============ 管理员：获取所有订单 ============

@router.get("/admin/list", response_model=OrderListResponse)
async def get_all_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """获取所有订单（管理员）"""
    query = select(Order)

    if status:
        query = query.where(Order.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.options(selectinload(Order.items))
    query = query.order_by(Order.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    orders = result.scalars().all()

    return OrderListResponse(
        items=orders,
        total=total,
        page=page,
        page_size=page_size
    )
