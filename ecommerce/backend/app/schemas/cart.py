"""
胖虫电商系统 - 购物车相关 Schema
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID
from decimal import Decimal


class CartItemAdd(BaseModel):
    """添加商品到购物车"""
    product_id: UUID = Field(..., description="商品ID")
    quantity: int = Field(1, ge=1, le=99, description="数量")


class CartItemUpdate(BaseModel):
    """更新购物车商品数量"""
    quantity: int = Field(..., ge=1, le=99, description="数量")


class CartItemResponse(BaseModel):
    """购物车商品响应"""
    id: UUID
    product_id: UUID
    product_name: str
    product_brand: Optional[str] = None
    product_model: Optional[str] = None
    product_description: Optional[str] = None
    product_specs: Optional[dict] = None
    product_image: Optional[str] = None
    product_price: Decimal
    product_original_price: Optional[Decimal] = None
    product_stock: int = 0
    quantity: int
    subtotal: Decimal
    is_in_stock: bool

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    """购物车响应"""
    items: List[CartItemResponse]
    total_items: int
    total_amount: Decimal


class CartMergeRequest(BaseModel):
    """合并购物车请求（登录后合并未登录时的购物车）"""
    session_id: str = Field(..., description="未登录时的会话ID")
