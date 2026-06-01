"""
胖虫电商系统 - 订单模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_no = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)

    # 金额信息
    total_amount = Column(Numeric(10, 2), nullable=False)
    shipping_fee = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    final_amount = Column(Numeric(10, 2), nullable=False)

    # 收货信息（快照）
    recipient_name = Column(String(50))
    recipient_phone = Column(String(20))
    shipping_address = Column(Text)

    # 支付信息
    payment_method = Column(String(20))  # alipay, wechat
    payment_id = Column(String(100))     # 第三方支付流水号
    paid_at = Column(DateTime(timezone=True))

    # 物流信息
    shipping_company = Column(String(50))
    tracking_number = Column(String(50))
    shipped_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # 备注
    remark = Column(Text)
    admin_note = Column(Text)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    # 状态约束
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded')",
            name="valid_order_status"
        ),
    )

    def __repr__(self):
        return f"<Order {self.order_no} status={self.status}>"

    @property
    def status_display(self) -> str:
        """状态中文显示"""
        status_map = {
            "pending": "待支付",
            "paid": "已支付",
            "shipped": "已发货",
            "completed": "已完成",
            "cancelled": "已取消",
            "refunded": "已退款"
        }
        return status_map.get(self.status, self.status)

    @property
    def is_paid(self) -> bool:
        """是否已支付"""
        return self.status in ("paid", "shipped", "completed")

    @property
    def can_cancel(self) -> bool:
        """是否可以取消"""
        return self.status == "pending"


class OrderItem(Base):
    """订单商品模型"""
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=True)
    item_type = Column(String(20), nullable=False, default="product")
    product_name = Column(String(200), nullable=False)  # 商品名称快照
    product_image = Column(String(500))  # 商品图片快照
    product_specs = Column(JSONB)
    price = Column(Numeric(10, 2), nullable=False)  # 下单时价格
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)  # 小计
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # 关联
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"
