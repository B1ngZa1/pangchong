"""
胖虫电商系统 - 外部行情 API
"""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import get_db
from ..models.product import Product, PriceHistory
from ..schemas.market import PriceHistoryResponse, PricePoint

router = APIRouter(prefix="/market", tags=["行情"])


def _to_decimal_price(value: Any) -> Optional[Decimal]:
    try:
        if value in (None, ""):
            return None
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except Exception:
        return None


def _extract_price_points(payload: dict[str, Any], days: int) -> list[PricePoint]:
    candidates = (
        payload.get("data", {}).get("list"),
        payload.get("data", {}).get("prices"),
        payload.get("data", {}).get("history"),
        payload.get("list"),
        payload.get("prices"),
        payload.get("history"),
    )
    rows = next((item for item in candidates if isinstance(item, list)), [])
    points: list[PricePoint] = []

    for row in rows:
        if isinstance(row, dict):
            raw_date = row.get("date") or row.get("time") or row.get("day")
            raw_price = row.get("price") or row.get("sale_price") or row.get("value")
        elif isinstance(row, (list, tuple)) and len(row) >= 2:
            raw_date, raw_price = row[0], row[1]
        else:
            continue

        price = _to_decimal_price(raw_price)
        if not price:
            continue

        try:
            point_date = date.fromisoformat(str(raw_date)[:10])
        except ValueError:
            continue
        points.append(PricePoint(date=point_date, price=price, source_name="TMAPI"))

    return sorted(points, key=lambda point: point.date)[-days:]


async def _fetch_tmapi_history(product: Product, days: int) -> list[PricePoint]:
    specs = product.specs or {}
    external_item_id = specs.get("external_item_id") or specs.get("tmapi_item_id")
    if not external_item_id or not settings.PRICE_HISTORY_API_KEY:
        return []

    params = {
        "apiToken": settings.PRICE_HISTORY_API_KEY,
        "itemId": external_item_id,
        "days": days,
    }
    platform = specs.get("price_platform")
    if platform:
        params["platform"] = platform

    async with httpx.AsyncClient(timeout=settings.PRICE_HISTORY_TIMEOUT_SECONDS) as client:
        response = await client.get(settings.PRICE_HISTORY_API_BASE_URL, params=params)
        response.raise_for_status()
    return _extract_price_points(response.json(), days)


@router.get("/price-history/{product_id}", response_model=PriceHistoryResponse)
async def get_price_history(
    product_id: UUID,
    days: int = Query(30, ge=7, le=360, description="价格走势天数"),
    db: AsyncSession = Depends(get_db),
):
    """获取有来源的真实价格走势；无数据时返回 unavailable。"""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在",
        )

    provider = settings.PRICE_HISTORY_PROVIDER.lower()
    points: list[PricePoint] = []
    source = "unavailable"

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    history_result = await db.execute(
        select(PriceHistory)
        .where(
            PriceHistory.product_id == product.id,
            PriceHistory.created_at >= cutoff,
        )
        .order_by(PriceHistory.created_at.asc())
    )
    history = history_result.scalars().all()
    if history:
        points = [
            PricePoint(
                date=item.created_at.date(),
                price=item.price,
                source_name=item.source_name,
                source_url=item.source_url,
            )
            for item in history
        ]
        source = "database"

    if not points and provider == "tmapi":
        try:
            points = await _fetch_tmapi_history(product, days)
            if points:
                source = "external-provider"
        except httpx.HTTPError:
            points = []

    return PriceHistoryResponse(
        product_id=str(product.id),
        provider=provider,
        source=source,
        days=len(points),
        points=points,
        external_item_id=(product.specs or {}).get("external_item_id"),
        recommendation=(
            "历史价格来自可审计记录。"
            if points
            else "暂无可靠历史价格；请通过管理员核价或配置外部行情提供商。"
        ),
    )
