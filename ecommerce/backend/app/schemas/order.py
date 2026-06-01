"""
胖虫电商系统 - 订单相关 Schema
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class CustomOrderItemCreate(BaseModel):
    """本地定制商品下单快照"""
    product_name: str = Field(..., min_length=1, max_length=200)
    product_image: Optional[str] = Field(None, max_length=500)
    product_specs: Optional[Dict[str, Any]] = None
    price: Decimal = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=99)


class OrderCreate(BaseModel):
    """创建订单请求"""
    address_id: UUID = Field(..., description="收货地址ID")
    remark: Optional[str] = Field(None, max_length=500, description="订单备注")
    cart_item_ids: Optional[List[UUID]] = Field(None, description="购物车商品ID列表，为空则结算全部")
    custom_items: Optional[List[CustomOrderItemCreate]] = Field(None, description="本地定制商品快照")


class OrderItemResponse(BaseModel):
    """订单商品响应"""
    id: UUID
    product_id: Optional[UUID]
    item_type: str = "product"
    product_name: str
    product_image: Optional[str]
    product_specs: Optional[Dict[str, Any]] = None
    price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """订单响应"""
    id: UUID
    order_no: str
    status: OrderStatus
    status_display: str
    total_amount: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    recipient_name: Optional[str]
    recipient_phone: Optional[str]
    shipping_address: Optional[str]
    payment_method: Optional[str]
    paid_at: Optional[datetime]
    shipping_company: Optional[str]
    tracking_number: Optional[str]
    shipped_at: Optional[datetime]
    completed_at: Optional[datetime]
    remark: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """订单列表响应"""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int


class OrderPayRequest(BaseModel):
    """订单支付请求"""
    payment_method: str = Field(..., pattern="^(alipay|wechat)$", description="支付方式")


class OrderShipRequest(BaseModel):
    """订单发货请求（管理员）"""
    shipping_company: str = Field(..., max_length=50, description="物流公司")
    tracking_number: str = Field(..., max_length=50, description="物流单号")


class OrderCancelRequest(BaseModel):
    """取消订单"""
    reason: Optional[str] = Field(None, max_length=200, description="取消原因")
