"""
胖虫电商系统 - 商品模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Category(Base):
    """商品分类模型"""
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    icon = Column(String(50))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # 关联
    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    """商品模型"""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2))
    cost_price = Column(Numeric(10, 2))
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)
    brand = Column(String(50))
    model = Column(String(100))
    stock = Column(Integer, nullable=False, default=0)
    sold_count = Column(Integer, default=0)
    image_url = Column(String(500))
    images = Column(JSONB)  # 商品图片数组
    specs = Column(JSONB)   # 商品规格参数
    model_3d_url = Column(String(500))
    model_3d_scale = Column(Numeric(8, 4), default=1)
    model_3d_position = Column(JSONB)  # [x, y, z]
    model_3d_rotation = Column(JSONB)  # [x, y, z]，单位为弧度
    asset_license = Column(String(100))
    asset_source_url = Column(String(500))
    price_source_name = Column(String(100))
    price_source_url = Column(String(500))
    price_checked_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    weight = Column(Numeric(8, 2))  # 重量(kg)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}>"

    @property
    def is_in_stock(self) -> bool:
        """是否有库存"""
        return self.stock > 0

    @property
    def discount_percent(self) -> float:
        """折扣百分比"""
        if self.original_price and self.original_price > 0:
            return round((1 - float(self.price) / float(self.original_price)) * 100, 1)
        return 0.0


class PriceHistory(Base):
    """有来源、可审计的商品历史价格。"""
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    source_name = Column(String(100))
    source_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    product = relationship("Product", back_populates="price_history")
