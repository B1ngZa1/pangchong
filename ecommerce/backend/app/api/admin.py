"""
胖虫电商系统 - 管理员 API
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, cast, Date
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID, uuid4
from pathlib import Path
from datetime import datetime, timedelta

from ..core.database import get_db
from ..core.security import get_current_admin
from ..models.user import User, UserAddress
from ..models.product import Product, Category
from ..models.order import Order, OrderItem
from ..models.cart import CartItem
from ..core.config import settings
from ..services.storage import StorageNotConfigured, StorageUploadError, storage_service

router = APIRouter(prefix="/admin", tags=["管理员"])


class StatusUpdate(BaseModel):
    is_active: bool


class ShipOrderRequest(BaseModel):
    shipping_company: str = Field(..., max_length=50)
    tracking_number: str = Field(..., max_length=50)


ASSET_RULES = {
    ".png": ("image/png", 5 * 1024 * 1024, "image"),
    ".jpg": ("image/jpeg", 5 * 1024 * 1024, "image"),
    ".jpeg": ("image/jpeg", 5 * 1024 * 1024, "image"),
    ".webp": ("image/webp", 5 * 1024 * 1024, "image"),
    ".glb": ("model/gltf-binary", 20 * 1024 * 1024, "model"),
}


def _has_valid_signature(data: bytes, suffix: str) -> bool:
    signatures = {
        ".png": data.startswith(b"\x89PNG\r\n\x1a\n"),
        ".jpg": data.startswith(b"\xff\xd8\xff"),
        ".jpeg": data.startswith(b"\xff\xd8\xff"),
        ".webp": len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP",
        ".glb": len(data) >= 12 and data[:4] == b"glTF" and int.from_bytes(data[4:8], "little") == 2,
    }
    return signatures.get(suffix, False)


@router.post("/assets", status_code=status.HTTP_201_CREATED)
async def upload_catalog_asset(
    bucket: str = Form(...),
    file: UploadFile = File(...),
    admin=Depends(get_current_admin),
):
    """Upload a validated catalog image or GLB through the trusted backend."""
    del admin
    suffix = Path(file.filename or "").suffix.lower()
    rule = ASSET_RULES.get(suffix)
    if not rule:
        raise HTTPException(status_code=415, detail="仅支持 PNG、JPEG、WebP 和 GLB")

    expected_mime, max_size, asset_kind = rule
    expected_bucket = settings.SUPABASE_MODEL_BUCKET if asset_kind == "model" else settings.SUPABASE_IMAGE_BUCKET
    if bucket != expected_bucket:
        raise HTTPException(status_code=400, detail="文件类型与目标 Bucket 不匹配")
    if file.content_type not in {expected_mime, "application/octet-stream"}:
        raise HTTPException(status_code=415, detail="文件 MIME 类型不匹配")

    data = await file.read(max_size + 1)
    await file.close()
    if len(data) > max_size:
        raise HTTPException(status_code=413, detail=f"文件超过 {max_size // (1024 * 1024)} MB 限制")
    if not data or not _has_valid_signature(data, suffix):
        raise HTTPException(status_code=415, detail="文件内容与扩展名不匹配")

    folder = "diy" if asset_kind == "model" else "products"
    object_path = f"{folder}/{uuid4().hex}{suffix}"
    try:
        asset = await storage_service.upload(
            bucket=bucket,
            path=object_path,
            data=data,
            mime_type=expected_mime,
        )
    except StorageNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except StorageUploadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return asset.to_dict()


# ============ 数据概览 ============

@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """获取仪表盘统计数据"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 总用户数
    total_users = await db.scalar(select(func.count()).select_from(User))

    # 今日新增用户
    today_users = await db.scalar(
        select(func.count()).select_from(User).where(User.created_at >= today_start)
    )

    # 总商品数
    total_products = await db.scalar(
        select(func.count()).select_from(Product).where(Product.is_active == True)
    )

    # 总订单数
    total_orders = await db.scalar(select(func.count()).select_from(Order))

    # 今日订单数
    today_orders = await db.scalar(
        select(func.count()).select_from(Order).where(Order.created_at >= today_start)
    )

    # 待发货订单数
    pending_shipment = await db.scalar(
        select(func.count()).select_from(Order).where(Order.status == "paid")
    )

    # 待付款订单数
    pending_payment = await db.scalar(
        select(func.count()).select_from(Order).where(Order.status == "pending")
    )

    # 总销售额
    total_revenue = await db.scalar(
        select(func.coalesce(func.sum(Order.final_amount), 0))
        .where(Order.status.in_(["paid", "shipped", "completed"]))
    )

    # 今日销售额
    today_revenue = await db.scalar(
        select(func.coalesce(func.sum(Order.final_amount), 0))
        .where(
            Order.status.in_(["paid", "shipped", "completed"]),
            Order.created_at >= today_start
        )
    )

    # 本月销售额
    month_revenue = await db.scalar(
        select(func.coalesce(func.sum(Order.final_amount), 0))
        .where(
            Order.status.in_(["paid", "shipped", "completed"]),
            Order.created_at >= month_start
        )
    )

    # 最近7天每日订单数和销售额
    daily_stats = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        next_day = day + timedelta(days=1)

        day_orders = await db.scalar(
            select(func.count()).select_from(Order).where(
                Order.created_at >= day, Order.created_at < next_day
            )
        )
        day_revenue = await db.scalar(
            select(func.coalesce(func.sum(Order.final_amount), 0)).where(
                Order.status.in_(["paid", "shipped", "completed"]),
                Order.created_at >= day, Order.created_at < next_day
            )
        )
        daily_stats.append({
            "date": day.strftime("%m-%d"),
            "orders": day_orders or 0,
            "revenue": float(day_revenue or 0),
        })

    # 订单状态分布
    status_counts = {}
    for s in ["pending", "paid", "shipped", "completed", "cancelled"]:
        count = await db.scalar(
            select(func.count()).select_from(Order).where(Order.status == s)
        )
        status_counts[s] = count or 0

    # 热销商品 TOP 5
    hot_products_result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .order_by(Product.sold_count.desc())
        .limit(5)
    )
    hot_products = [
        {
            "id": str(p.id),
            "name": p.name,
            "sold_count": p.sold_count,
            "price": float(p.price),
            "image_url": p.image_url,
        }
        for p in hot_products_result.scalars().all()
    ]

    return {
        "total_users": total_users or 0,
        "today_users": today_users or 0,
        "total_products": total_products or 0,
        "total_orders": total_orders or 0,
        "today_orders": today_orders or 0,
        "pending_shipment": pending_shipment or 0,
        "pending_payment": pending_payment or 0,
        "total_revenue": float(total_revenue or 0),
        "today_revenue": float(today_revenue or 0),
        "month_revenue": float(month_revenue or 0),
        "daily_stats": daily_stats,
        "order_status_counts": status_counts,
        "hot_products": hot_products,
    }


# ============ 用户管理 ============

@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索用户名/邮箱/手机"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """获取用户列表"""
    query = select(User)

    if keyword:
        query = query.where(
            User.username.ilike(f"%{keyword}%") |
            User.email.ilike(f"%{keyword}%") |
            User.phone.ilike(f"%{keyword}%")
        )

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "items": [
            {
                "id": str(u.id),
                "username": u.username,
                "email": u.email,
                "phone": u.phone,
                "nickname": u.nickname,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: UUID,
    payload: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """启用/禁用用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.is_admin:
        raise HTTPException(status_code=400, detail="不能修改管理员状态")

    user.is_active = payload.is_active
    await db.flush()
    return {"message": f"用户已{'启用' if payload.is_active else '禁用'}"}


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """获取用户详情"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户地址
    addr_result = await db.execute(
        select(UserAddress).where(UserAddress.user_id == user_id)
    )
    addresses = addr_result.scalars().all()

    # 获取用户订单数和总消费
    order_count = await db.scalar(
        select(func.count()).select_from(Order).where(Order.user_id == user_id)
    )
    total_spent = await db.scalar(
        select(func.coalesce(func.sum(Order.final_amount), 0))
        .where(Order.user_id == user_id, Order.status.in_(["paid", "shipped", "completed"]))
    )

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "addresses": [
            {
                "id": str(a.id),
                "recipient_name": a.recipient_name,
                "phone": a.phone,
                "province": a.province,
                "city": a.city,
                "district": a.district,
                "address": a.address,
                "is_default": a.is_default,
            }
            for a in addresses
        ],
        "order_count": order_count or 0,
        "total_spent": float(total_spent or 0),
    }


# ============ 订单管理（扩展） ============

@router.get("/orders")
async def get_all_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="订单状态"),
    keyword: Optional[str] = Query(None, description="搜索订单号/用户名"),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """获取所有订单（支持搜索）"""
    query = select(Order).options(selectinload(Order.items))

    if status:
        query = query.where(Order.status == status)

    if keyword:
        query = query.where(
            Order.order_no.ilike(f"%{keyword}%") |
            Order.recipient_name.ilike(f"%{keyword}%") |
            Order.recipient_phone.ilike(f"%{keyword}%")
        )

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页
    query = query.order_by(Order.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    orders = result.scalars().all()

    return {
        "items": [
            {
                "id": str(o.id),
                "order_no": o.order_no,
                "status": o.status,
                "status_display": o.status_display,
                "total_amount": float(o.total_amount),
                "shipping_fee": float(o.shipping_fee),
                "discount_amount": float(o.discount_amount),
                "final_amount": float(o.final_amount),
                "recipient_name": o.recipient_name,
                "recipient_phone": o.recipient_phone,
                "shipping_address": o.shipping_address,
                "payment_method": o.payment_method,
                "paid_at": o.paid_at.isoformat() if o.paid_at else None,
                "shipping_company": o.shipping_company,
                "tracking_number": o.tracking_number,
                "shipped_at": o.shipped_at.isoformat() if o.shipped_at else None,
                "remark": o.remark,
                "item_count": len(o.items),
                "items": [
                    {
                        "id": str(item.id),
                        "product_id": str(item.product_id) if item.product_id else None,
                        "item_type": item.item_type,
                        "product_name": item.product_name,
                        "product_image": item.product_image,
                        "product_specs": item.product_specs,
                        "price": float(item.price),
                        "quantity": item.quantity,
                        "subtotal": float(item.subtotal),
                    }
                    for item in o.items
                ],
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "updated_at": o.updated_at.isoformat() if o.updated_at else None,
            }
            for o in orders
        ],
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


@router.get("/orders/{order_id}")
async def get_order_detail(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """获取订单详情（管理员）"""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 获取用户信息
    user_result = await db.execute(select(User).where(User.id == order.user_id))
    user = user_result.scalar_one_or_none()

    return {
        "id": str(order.id),
        "order_no": order.order_no,
        "status": order.status,
        "status_display": order.status_display,
        "total_amount": float(order.total_amount),
        "shipping_fee": float(order.shipping_fee),
        "discount_amount": float(order.discount_amount),
        "final_amount": float(order.final_amount),
        "recipient_name": order.recipient_name,
        "recipient_phone": order.recipient_phone,
        "shipping_address": order.shipping_address,
        "payment_method": order.payment_method,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "shipping_company": order.shipping_company,
        "tracking_number": order.tracking_number,
        "shipped_at": order.shipped_at.isoformat() if order.shipped_at else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        "remark": order.remark,
        "items": [
            {
                "id": str(item.id),
                "product_id": str(item.product_id) if item.product_id else None,
                "item_type": item.item_type,
                "product_name": item.product_name,
                "product_image": item.product_image,
                "product_specs": item.product_specs,
                "price": float(item.price),
                "quantity": item.quantity,
                "subtotal": float(item.subtotal),
            }
            for item in order.items
        ],
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "nickname": user.nickname,
        } if user else None,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }


@router.post("/orders/{order_id}/ship")
async def ship_order(
    order_id: UUID,
    payload: ShipOrderRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """订单发货"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status != "paid":
        raise HTTPException(status_code=400, detail="只有已支付的订单才能发货")

    order.status = "shipped"
    order.shipping_company = payload.shipping_company
    order.tracking_number = payload.tracking_number
    order.shipped_at = datetime.utcnow()

    await db.flush()
    return {"message": "发货成功", "order_no": order.order_no}


# ============ 商品管理（扩展） ============

@router.get("/products")
async def get_all_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索商品名/品牌/型号"),
    category_id: Optional[UUID] = Query(None, description="分类ID"),
    is_active: Optional[bool] = Query(None, description="是否上架"),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """获取所有商品（管理员，包含下架商品）"""
    query = select(Product)

    if keyword:
        query = query.where(
            Product.name.ilike(f"%{keyword}%") |
            Product.brand.ilike(f"%{keyword}%") |
            Product.model.ilike(f"%{keyword}%")
        )

    if category_id:
        query = query.where(Product.category_id == category_id)

    if is_active is not None:
        query = query.where(Product.is_active == is_active)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 分页
    query = query.order_by(Product.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    products = result.scalars().all()

    return {
        "items": [
            {
                "id": str(p.id),
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "price": float(p.price),
                "original_price": float(p.original_price) if p.original_price else None,
                "cost_price": float(p.cost_price) if p.cost_price else None,
                "category_id": str(p.category_id) if p.category_id else None,
                "brand": p.brand,
                "model": p.model,
                "stock": p.stock,
                "sold_count": p.sold_count,
                "image_url": p.image_url,
                "is_active": p.is_active,
                "is_featured": p.is_featured,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in products
        ],
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


@router.put("/products/{product_id}/status")
async def toggle_product_status(
    product_id: UUID,
    payload: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """上架/下架商品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    product.is_active = payload.is_active
    await db.flush()
    return {"message": f"商品已{'上架' if payload.is_active else '下架'}"}


# ============ 分类管理 ============

@router.get("/categories")
async def get_all_categories(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """获取所有分类（包含非活跃）"""
    result = await db.execute(
        select(Category).order_by(Category.sort_order)
    )
    categories = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "icon": c.icon,
            "parent_id": str(c.parent_id) if c.parent_id else None,
            "sort_order": c.sort_order,
            "is_active": c.is_active,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in categories
    ]
