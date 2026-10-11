"""Durable payment notification records."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class PaymentEvent(Base):
    """A verified provider notification and its idempotent application result.

    The original callback is deliberately not persisted.  The event keeps only
    the identifiers and a digest needed for reconciliation and replay checks.
    """

    __tablename__ = "payment_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(32), nullable=False, default="alipay")
    event_key = Column(String(128), nullable=False)
    dedupe_key = Column(String(64), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False)
    order_no = Column(String(32), nullable=False, index=True)
    trade_no = Column(String(100), nullable=False, index=True)
    notification_id = Column(String(128), nullable=True)
    trade_status = Column(String(32), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    processing_result = Column(String(32), nullable=False)
    received_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    applied_at = Column(DateTime(timezone=True), nullable=True)

    order = relationship("Order", back_populates="payment_events")

    __table_args__ = (
        UniqueConstraint("provider", "event_key", name="uq_payment_events_provider_event_key"),
        UniqueConstraint("provider", "dedupe_key", name="uq_payment_events_provider_dedupe_key"),
        Index("idx_payment_events_order_id", "order_id"),
        Index("idx_payment_events_trade_no", "provider", "trade_no"),
    )

    def __repr__(self) -> str:
        return f"<PaymentEvent {self.provider}:{self.trade_no} {self.trade_status}>"
