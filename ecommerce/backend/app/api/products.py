"""
胖虫电商系统 - 商品 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, exc as sa_exc
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_current_user, get_current_admin
from ..models.product import Product, Category
from ..schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductBrief,
    CategoryCreate,
    CategoryResponse,
)

router = APIRouter(prefix="/products", tags=["商品"])


# ============ 分类 ============

@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取所有分类"""
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.sort_order)
    )
    return result.scalars().all()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """创建分类（管理员）"""
    # 检查 slug 是否已存在
    result = await db.execute(select(Category).where(Category.slug == category_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类标识已存在"
        )

    category = Category(**category_data.dict())
    db.add(category)
    await db.flush()
    return category


# ============ 商品列表 ============

@router.get("", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category_id: Optional[UUID] = Query(None, description="分类ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    brand: Optional[str] = Query(None, description="品牌"),
    spec_key: Optional[str] = Query(None, max_length=50, description="规格字段，例如 capacity/socket/form_factor"),
    spec_value: Optional[str] = Query(None, max_length=100, description="规格值，支持模糊匹配"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
    is_featured: Optional[bool] = Query(None, description="是否推荐"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品列表

    支持分页、筛选、搜索、排序
    """
    # 构建查询
    query = select(Product).where(Product.is_active == True)

    # 分类筛选
    if category_id:
        query = query.where(Product.category_id == category_id)

    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                Product.name.ilike(f"%{keyword}%"),
                Product.brand.ilike(f"%{keyword}%"),
                Product.model.ilike(f"%{keyword}%"),
                Product.description.ilike(f"%{keyword}%"),
            )
        )

    # 品牌筛选
    if brand:
        query = query.where(Product.brand == brand)

    # 规格筛选：用于 DIY 配件按容量、插槽、板型、电源规格等字段过滤
    if spec_key and spec_value:
        query = query.where(Product.specs.op("->>")(spec_key).ilike(f"%{spec_value}%"))

    # 价格范围
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)

    # 推荐筛选
    if is_featured is not None:
        query = query.where(Product.is_featured == is_featured)

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # 排序（白名单限制可排序字段）
    ALLOWED_SORT_FIELDS = {"created_at", "price", "sold_count", "name", "stock"}
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = "created_at"
    sort_column = getattr(Product, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)

    # 执行查询
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """通过 slug 获取商品详情（仅上架商品）"""
    result = await db.execute(
        select(Product).where(Product.slug == slug, Product.is_active == True)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    return product


# ============ 热门/推荐商品 ============

@router.get("/featured/list", response_model=list[ProductBrief])
async def get_featured_products(
    limit: int = Query(10, ge=1, le=50, description="数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取推荐商品"""
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True, Product.is_featured == True)
        .order_by(Product.sold_count.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/hot/list", response_model=list[ProductBrief])
async def get_hot_products(
    limit: int = Query(10, ge=1, le=50, description="数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取热门商品（按销量排序）"""
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .order_by(Product.sold_count.desc())
        .limit(limit)
    )
    return result.scalars().all()


# ============ 商品详情 ============

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取商品详情（仅上架商品）"""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    return product


# ============ 管理员操作 ============

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """创建商品（管理员）"""
    # 检查 slug 是否已存在
    result = await db.execute(select(Product).where(Product.slug == product_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品标识已存在"
        )

    product = Product(**product_data.dict())
    db.add(product)
    await db.flush()
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """更新商品（管理员）"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    # 如果更新 slug，检查唯一性
    update_data = product_data.dict(exclude_unset=True)
    if "slug" in update_data and update_data["slug"] != product.slug:
        result = await db.execute(select(Product).where(Product.slug == update_data["slug"]))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="商品标识已存在"
            )

    # 更新字段
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.flush()
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """删除商品（管理员，软删除）"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    product.is_active = False
    await db.flush()
    return {"message": "商品已下架"}
