"""
胖虫电商系统 - 订单 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID
from datetime import datetime
import random
import string
import uuid

from ..core.database import get_db
from ..core.security import get_current_user, get_current_admin
from ..core.config import settings
from ..models.user import User, UserAddress
from ..models.product import Product
from ..models.cart import CartItem
from ..models.order import Order, OrderItem
from ..schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderPayRequest,
    OrderShipRequest,
    OrderCancelRequest,
)

router = APIRouter(prefix="/orders", tags=["订单"])


def generate_order_no() -> str:
    """生成订单号：PC + 时间戳 + UUID 片段（避免碰撞）"""
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    unique = uuid.uuid4().hex[:8].upper()
    return f"PC{now}{unique}"


def calculate_shipping_fee(amount: float) -> float:
    """计算运费"""
    if amount >= settings.FREE_SHIPPING_THRESHOLD:
        return 0.0
    return settings.SHIPPING_FEE


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
    # 获取收货地址
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == order_data.address_id,
            UserAddress.user_id == current_user.id
        )
    )
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收货地址不存在"
        )

    # 获取购物车商品
    query = select(CartItem).options(selectinload(CartItem.product)).where(
        CartItem.user_id == current_user.id
    )
    if order_data.cart_item_ids is not None:
        query = query.where(CartItem.id.in_(order_data.cart_item_ids))

    result = await db.execute(query)
    cart_items = result.scalars().all()
    custom_items = order_data.custom_items or []

    if not cart_items and not custom_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="购物车为空"
        )

    # 验证库存并计算金额
    total_amount = 0
    order_items = []

    for cart_item in cart_items:
        product = cart_item.product

        # 检查商品是否上架
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 {product.name} 已下架"
            )

        # 检查库存（使用 SELECT FOR UPDATE 防止并发超卖）
        result = await db.execute(
            select(Product).where(Product.id == product.id).with_for_update()
        )
        product = result.scalar_one()

        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 {product.name} 库存不足，当前库存：{product.stock}"
            )

        subtotal = float(product.price) * cart_item.quantity
        total_amount += subtotal

        order_items.append({
            "item_type": "product",
            "product": product,
            "product_name": product.name,
            "product_image": product.image_url,
            "product_specs": product.specs,
            "quantity": cart_item.quantity,
            "price": float(product.price),
            "subtotal": subtotal,
        })

    for custom_item in custom_items:
        price = float(custom_item.price)
        subtotal = price * custom_item.quantity
        total_amount += subtotal

        order_items.append({
            "item_type": "custom",
            "product": None,
            "product_name": custom_item.product_name,
            "product_image": custom_item.product_image,
            "product_specs": custom_item.product_specs or {},
            "quantity": custom_item.quantity,
            "price": price,
            "subtotal": subtotal,
        })

    # 计算运费
    shipping_fee = calculate_shipping_fee(total_amount)
    final_amount = total_amount + shipping_fee

    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        user_id=current_user.id,
        status="pending",
        total_amount=total_amount,
        shipping_fee=shipping_fee,
        discount_amount=0,
        final_amount=final_amount,
        recipient_name=address.recipient_name,
        recipient_phone=address.phone,
        shipping_address=f"{address.province}{address.city}{address.district}{address.address}",
        remark=order_data.remark,
    )
    db.add(order)
    await db.flush()

    # 创建订单商品
    for item_data in order_items:
        product = item_data["product"]
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id if product else None,
            item_type=item_data["item_type"],
            product_name=item_data["product_name"],
            product_image=item_data["product_image"],
            product_specs=item_data["product_specs"],
            price=item_data["price"],
            quantity=item_data["quantity"],
            subtotal=item_data["subtotal"],
        )
        db.add(order_item)

        # 扣减库存
        if product:
            product.stock -= item_data["quantity"]
            product.sold_count += item_data["quantity"]

    # 清空购物车中已下单的商品
    for cart_item in cart_items:
        await db.delete(cart_item)

    await db.flush()

    # 重新查询订单以获取完整数据
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order.id)
    )
    order = result.scalar_one()

    return order


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

    # 恢复库存
    for item in order.items:
        if not item.product_id:
            continue
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalar_one_or_none()
        if product:
            product.stock += item.quantity
            product.sold_count -= item.quantity

    # 更新订单状态
    order.status = "cancelled"
    order.remark = f"{order.remark or ''}\n取消原因：{cancel_data.reason or '用户主动取消'}"

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
