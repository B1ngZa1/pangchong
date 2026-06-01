"""
胖虫电商系统 - 行情相关 Schema
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class PricePoint(BaseModel):
    """单日价格点"""
    date: date
    price: Decimal


class PriceHistoryResponse(BaseModel):
    """商品价格走势响应"""
    product_id: str
    provider: str
    source: str
    currency: str = "CNY"
    days: int
    points: List[PricePoint]
    recommendation: str
    external_item_id: Optional[str] = None
