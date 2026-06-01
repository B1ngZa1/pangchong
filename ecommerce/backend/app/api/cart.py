"""
胖虫电商系统 - 购物车 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_current_user, get_current_user_optional
from ..models.user import User
from ..models.product import Product
from ..models.cart import CartItem
from ..schemas.cart import (
    CartItemAdd,
    CartItemUpdate,
    CartItemResponse,
    CartResponse,
    CartMergeRequest,
)

router = APIRouter(prefix="/cart", tags=["购物车"])


def get_cart_query(user_id: Optional[UUID] = None, session_id: Optional[str] = None):
    """获取购物车查询条件"""
    if user_id:
        return CartItem.user_id == user_id
    elif session_id:
        return CartItem.session_id == session_id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="需要用户ID或会话ID"
        )


async def get_cart_items(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
    session_id: Optional[str] = None
) -> list:
    """获取购物车商品列表"""
    query = select(CartItem).options(selectinload(CartItem.product))
    if user_id:
        query = query.where(CartItem.user_id == user_id)
    elif session_id:
        query = query.where(CartItem.session_id == session_id)
    else:
        return []

    result = await db.execute(query)
    return result.scalars().all()


def format_cart_item(item: CartItem) -> CartItemResponse:
    """格式化购物车商品响应"""
    if not item.product:
        return CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name="[商品已删除]",
            product_brand=None,
            product_model=None,
            product_description=None,
            product_specs=None,
            product_image=None,
            product_price=0,
            product_original_price=None,
            product_stock=0,
            quantity=item.quantity,
            subtotal=0,
            is_in_stock=False,
        )
    return CartItemResponse(
        id=item.id,
        product_id=item.product_id,
        product_name=item.product.name,
        product_brand=getattr(item.product, 'brand', None),
        product_model=getattr(item.product, 'model', None),
        product_description=getattr(item.product, 'description', None),
        product_specs=getattr(item.product, 'specs', None),
        product_image=item.product.image_url,
        product_price=item.product.price,
        product_original_price=getattr(item.product, 'original_price', None),
        product_stock=item.product.stock,
        quantity=item.quantity,
        subtotal=item.product.price * item.quantity,
        is_in_stock=item.product.stock >= item.quantity
    )


# ============ 获取购物车 ============

@router.get("", response_model=CartResponse)
async def get_cart(
    session_id: Optional[str] = Query(None, description="会话ID（未登录时使用）"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    获取购物车

    - 登录用户：获取用户购物车
    - 未登录：通过 session_id 获取临时购物车
    """
    user_id = current_user.id if current_user else None

    if not user_id and not session_id:
        return CartResponse(items=[], total_items=0, total_amount=0)

    items = await get_cart_items(db, user_id, session_id)

    cart_items = [format_cart_item(item) for item in items]
    total_items = sum(item.quantity for item in cart_items)
    total_amount = sum(item.subtotal for item in cart_items)

    return CartResponse(
        items=cart_items,
        total_items=total_items,
        total_amount=total_amount
    )


# ============ 添加商品到购物车 ============

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemAdd,
    session_id: Optional[str] = Query(None, description="会话ID（未登录时使用）"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    添加商品到购物车

    - **product_id**: 商品ID
    - **quantity**: 数量（默认1）
    """
    user_id = current_user.id if current_user else None

    if not user_id and not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="需要登录或提供会话ID"
        )

    # 检查商品是否存在且上架
    result = await db.execute(select(Product).where(Product.id == item_data.product_id))
    product = result.scalar_one_or_none()
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在或已下架"
        )

    # 检查库存
    if product.stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"库存不足，当前库存：{product.stock}"
        )

    # 检查购物车中是否已有该商品
    query = select(CartItem).where(CartItem.product_id == item_data.product_id)
    if user_id:
        query = query.where(CartItem.user_id == user_id)
    else:
        query = query.where(CartItem.session_id == session_id)

    result = await db.execute(query)
    existing_item = result.scalar_one_or_none()

    if existing_item:
        # 已存在，增加数量
        new_quantity = existing_item.quantity + item_data.quantity
        if product.stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存不足，当前库存：{product.stock}，购物车已有：{existing_item.quantity}"
            )
        existing_item.quantity = new_quantity
        await db.flush()
        return format_cart_item(existing_item)
    else:
        # 不存在，创建新项
        cart_item = CartItem(
            user_id=user_id,
            session_id=session_id if not user_id else None,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )
        db.add(cart_item)
        await db.flush()

        # 重新查询以获取关联数据
        result = await db.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.id == cart_item.id)
        )
        cart_item = result.scalar_one()
        return format_cart_item(cart_item)


# ============ 更新购物车商品数量 ============

@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: UUID,
    item_data: CartItemUpdate,
    session_id: Optional[str] = Query(None, description="会话ID（未登录时使用）"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    更新购物车商品数量

    - **quantity**: 新数量
    """
    # 查询购物车项
    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.id == item_id)
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物车项不存在"
        )

    # 验证权限（必须是所有者才能修改）
    if current_user and cart_item.user_id == current_user.id:
        pass
    elif cart_item.session_id and session_id == cart_item.session_id:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此购物车项"
        )

    # 检查库存
    if cart_item.product.stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"库存不足，当前库存：{cart_item.product.stock}"
        )

    cart_item.quantity = item_data.quantity
    await db.flush()
    return format_cart_item(cart_item)


# ============ 删除购物车商品 ============

@router.delete("/items/{item_id}")
async def remove_from_cart(
    item_id: UUID,
    session_id: Optional[str] = Query(None, description="会话ID（未登录时使用）"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """删除购物车中的商品"""
    result = await db.execute(select(CartItem).where(CartItem.id == item_id))
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="购物车项不存在"
        )

    # 验证权限
    if current_user and cart_item.user_id == current_user.id:
        pass
    elif cart_item.session_id and session_id == cart_item.session_id:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此购物车项"
        )

    await db.delete(cart_item)
    return {"message": "已从购物车移除"}


# ============ 清空购物车 ============

@router.delete("/clear")
async def clear_cart(
    session_id: Optional[str] = Query(None, description="会话ID（未登录时使用）"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """清空购物车"""
    user_id = current_user.id if current_user else None

    if not user_id and not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="需要登录或提供会话ID"
        )

    items = await get_cart_items(db, user_id, session_id)
    for item in items:
        await db.delete(item)

    return {"message": f"已清空购物车，共删除 {len(items)} 件商品"}


# ============ 合并购物车 ============

@router.post("/merge", response_model=CartResponse)
async def merge_cart(
    merge_data: CartMergeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    合并购物车（登录后合并未登录时的购物车）

    - **session_id**: 未登录时的会话ID
    """
    # 获取未登录时的购物车
    session_items = await get_cart_items(db, session_id=merge_data.session_id)

    if not session_items:
        # 没有需要合并的商品，返回当前用户购物车
        user_items = await get_cart_items(db, user_id=current_user.id)
        cart_items = [format_cart_item(item) for item in user_items]
        total_items = sum(item.quantity for item in cart_items)
        total_amount = sum(item.subtotal for item in cart_items)
        return CartResponse(items=cart_items, total_items=total_items, total_amount=total_amount)

    # 获取用户当前购物车
    user_items = await get_cart_items(db, user_id=current_user.id)
    user_product_ids = {item.product_id: item for item in user_items}

    # 合并逻辑
    for session_item in session_items:
        if session_item.product_id in user_product_ids:
            # 商品已存在，增加数量（检查库存上限）
            user_item = user_product_ids[session_item.product_id]
            if session_item.product and session_item.product.stock > 0:
                max_qty = session_item.product.stock
                user_item.quantity = min(user_item.quantity + session_item.quantity, max_qty)
            else:
                user_item.quantity += session_item.quantity
            # 删除会话项
            await db.delete(session_item)
        else:
            # 商品不存在，转移归属到用户（不删除）
            session_item.user_id = current_user.id
            session_item.session_id = None

    await db.flush()

    # 返回合并后的购物车
    user_items = await get_cart_items(db, user_id=current_user.id)
    cart_items = [format_cart_item(item) for item in user_items]
    total_items = sum(item.quantity for item in cart_items)
    total_amount = sum(item.subtotal for item in cart_items)

    return CartResponse(items=cart_items, total_items=total_items, total_amount=total_amount)
