"""Import verified reference prices without changing the store's sale price."""
import argparse
import asyncio
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="CSV produced from docs/data/price-verification.csv")
    return parser.parse_args()


def load_verified_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    verified = []
    for line, row in enumerate(rows, start=2):
        if row.get("status", "").strip().lower() != "verified":
            continue
        required = ["slug", "reference_price", "source_name", "source_url", "checked_at"]
        if any(not row.get(field, "").strip() for field in required):
            raise ValueError(f"第 {line} 行 verified 数据缺少必填字段")
        if not row["source_url"].startswith(("https://", "http://")):
            raise ValueError(f"第 {line} 行来源 URL 无效")
        try:
            row["parsed_price"] = Decimal(row["reference_price"]).quantize(Decimal("0.01"))
            row["parsed_checked_at"] = datetime.fromisoformat(row["checked_at"].replace("Z", "+00:00"))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"第 {line} 行价格或时间格式无效") from exc
        if row["parsed_price"] <= 0:
            raise ValueError(f"第 {line} 行价格必须大于 0")
        verified.append(row)
    return verified


async def import_rows(rows: list[dict]) -> tuple[int, int]:
    # Keep CSV validation and ``--help`` usable without bootstrapping the app.
    from sqlalchemy import select

    from ..core.database import AsyncSessionLocal
    from ..models.product import PriceHistory, Product

    imported = 0
    skipped = 0
    async with AsyncSessionLocal() as session:
        for row in rows:
            product = await session.scalar(select(Product).where(Product.slug == row["slug"]))
            if not product:
                raise ValueError(f"商品不存在：{row['slug']}")

            exists = await session.scalar(
                select(PriceHistory.id).where(
                    PriceHistory.product_id == product.id,
                    PriceHistory.created_at == row["parsed_checked_at"],
                    PriceHistory.source_url == row["source_url"],
                )
            )
            if exists:
                skipped += 1
                continue

            session.add(PriceHistory(
                product_id=product.id,
                price=row["parsed_price"],
                source_name=row["source_name"],
                source_url=row["source_url"],
                created_at=row["parsed_checked_at"],
            ))
            product.price_source_name = row["source_name"]
            product.price_source_url = row["source_url"]
            product.price_checked_at = row["parsed_checked_at"]
            imported += 1
        await session.commit()
    return imported, skipped


async def main() -> None:
    rows = load_verified_rows(parse_args().file)
    imported, skipped = await import_rows(rows)
    print(f"verified={len(rows)} imported={imported} skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(main())
