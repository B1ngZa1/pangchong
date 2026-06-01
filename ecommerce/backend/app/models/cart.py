"""
胖虫电商系统 - 购物车模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class CartItem(Base):
    """购物车商品模型"""
    __tablename__ = "cart_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

    # 唯一约束：同一用户/会话的同一商品只有一条记录
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="unique_user_product"),
        UniqueConstraint("session_id", "product_id", name="unique_session_product"),
    )

    def __repr__(self):
        return f"<CartItem user={self.user_id} product={self.product_id} qty={self.quantity}>"

    @property
    def subtotal(self) -> float:
        """小计金额"""
        return float(self.product.price) * self.quantity if self.product else 0
