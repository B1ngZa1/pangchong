"""
胖虫电商系统 - 商品相关 Schema
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============ 分类 ============

class CategoryBase(BaseModel):
    """分类基本信息"""
    name: str = Field(..., max_length=50, description="分类名称")
    slug: str = Field(..., max_length=50, description="分类标识")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    sort_order: int = Field(0, description="排序")


class CategoryCreate(CategoryBase):
    """创建分类"""
    parent_id: Optional[UUID] = None


class CategoryResponse(CategoryBase):
    """分类响应"""
    id: UUID
    parent_id: Optional[UUID]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ 商品 ============

class ProductBase(BaseModel):
    """商品基本信息"""
    model_config = ConfigDict(protected_namespaces=())
    name: str = Field(..., max_length=200, description="商品名称")
    slug: str = Field(..., max_length=200, description="商品标识")
    description: Optional[str] = Field(None, description="商品描述")
    price: Decimal = Field(..., ge=0, description="售价")
    original_price: Optional[Decimal] = Field(None, ge=0, description="原价")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="成本价")
    category_id: Optional[UUID] = Field(None, description="分类ID")
    brand: Optional[str] = Field(None, max_length=50, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="型号")
    stock: int = Field(0, ge=0, description="库存")
    image_url: Optional[str] = Field(None, max_length=500, description="主图URL")
    images: Optional[List[str]] = Field(None, description="图片列表")
    specs: Optional[Dict[str, Any]] = Field(None, description="规格参数")
    model_3d_url: Optional[str] = Field(None, max_length=500, description="GLB 模型 URL")
    model_3d_scale: Decimal = Field(Decimal("1"), gt=0, le=100, description="模型统一缩放")
    model_3d_position: Optional[List[float]] = Field(None, min_length=3, max_length=3)
    model_3d_rotation: Optional[List[float]] = Field(None, min_length=3, max_length=3)
    asset_license: Optional[str] = Field(None, max_length=100, description="3D/图片资产许可")
    price_source_name: Optional[str] = Field(None, max_length=100, description="价格来源名称")
    price_source_url: Optional[str] = Field(None, max_length=500, description="价格来源 URL")
    price_checked_at: Optional[datetime] = Field(None, description="最近核价时间")
    is_active: bool = Field(True, description="是否上架")
    is_featured: bool = Field(False, description="是否推荐")
    weight: Optional[Decimal] = Field(None, ge=0, description="重量(kg)")


class ProductCreate(ProductBase):
    """创建商品"""
    pass


class ProductUpdate(BaseModel):
    """更新商品"""
    model_config = ConfigDict(protected_namespaces=())
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    original_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    category_id: Optional[UUID] = None
    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=100)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = None
    specs: Optional[Dict[str, Any]] = None
    model_3d_url: Optional[str] = Field(None, max_length=500)
    model_3d_scale: Optional[Decimal] = Field(None, gt=0, le=100)
    model_3d_position: Optional[List[float]] = Field(None, min_length=3, max_length=3)
    model_3d_rotation: Optional[List[float]] = Field(None, min_length=3, max_length=3)
    asset_license: Optional[str] = Field(None, max_length=100)
    price_source_name: Optional[str] = Field(None, max_length=100)
    price_source_url: Optional[str] = Field(None, max_length=500)
    price_checked_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    weight: Optional[Decimal] = Field(None, ge=0)


class ProductResponse(ProductBase):
    """商品响应"""
    id: UUID
    sold_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ProductListResponse(BaseModel):
    """商品列表响应"""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ProductBrief(BaseModel):
    """商品简要信息（用于列表展示）"""
    id: UUID
    name: str
    slug: str
    price: Decimal
    original_price: Optional[Decimal]
    image_url: Optional[str]
    brand: Optional[str]
    sold_count: int
    is_in_stock: bool

    model_config = ConfigDict(from_attributes=True)
