"""Transactional order creation with authoritative server-side pricing."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping, Sequence
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import settings
from ..models.cart import CartItem
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..models.user import UserAddress
from ..schemas.order import CustomOrderItemCreate, OrderCreate
from .diy_catalog import DiyConfiguration, get_diy_configuration
from .diy_compatibility import evaluate_diy_compatibility
from .money import from_minor_units, to_minor_units


class OrderCreationError(Exception):
    def __init__(self, status_code: int, detail: str, *, payload: Mapping[str, Any] | None = None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.payload = payload


@dataclass(frozen=True)
class PricedOrderItem:
    item_type: str
    product_id: UUID | None
    product_name: str
    product_image: str | None
    product_specs: dict[str, Any]
    price_minor: int
    quantity: int
    subtotal_minor: int
    configuration_id: str | None = None
    configuration_version: int | None = None


@dataclass(frozen=True)
class PricedOrder:
    items: tuple[PricedOrderItem, ...]
    inventory: Mapping[UUID, int]
    total_minor: int


def _product_name(product: Product) -> str:
    return str(product.name)


def _validate_product_available(product: Product, required_quantity: int) -> None:
    if not product.is_active:
        raise OrderCreationError(400, f"Product {_product_name(product)} is delisted")
    if product.stock < required_quantity:
        raise OrderCreationError(
            400,
            f"Product {_product_name(product)} is out of stock; available: {product.stock}",
        )


def _diy_snapshot(
    item: CustomOrderItemCreate,
    configuration: DiyConfiguration,
    products: Mapping[UUID, Product],
    created_at: datetime,
) -> PricedOrderItem:
    references = item.configuration.parts
    slot_ids = [reference.slot_id for reference in references]
    if len(set(slot_ids)) != len(slot_ids):
        raise OrderCreationError(400, "DIY configuration contains duplicate slot IDs")
    if set(slot_ids) != set(configuration.slots):
        raise OrderCreationError(400, "DIY configuration must reference every required slot exactly once")

    variant = configuration.variants.get(item.configuration.variant_id)
    material = configuration.materials.get(item.configuration.material_id)
    if variant is None or material is None:
        raise OrderCreationError(400, "DIY configuration references an unknown appearance option")

    parts: list[dict[str, Any]] = []
    parts_total_minor = 0
    image_by_slot: dict[str, str | None] = {}
    products_by_slot: dict[str, Product] = {}
    for reference in references:
        slot = configuration.slots[reference.slot_id]
        product = products.get(reference.product_id)
        if product is None:
            raise OrderCreationError(400, f"DIY product {reference.product_id} does not exist")
        if product.category_id != slot.category_id:
            raise OrderCreationError(400, f"Product {_product_name(product)} does not belong in slot {slot.id}")

        price_minor = to_minor_units(product.price)
        parts_total_minor += price_minor * reference.quantity
        image_by_slot[slot.id] = product.image_url
        products_by_slot[slot.id] = product
        parts.append({
            "key": slot.id,
            "label": slot.label,
            "category_id": str(slot.category_id),
            "product_id": str(product.id),
            "name": product.name,
            "brand": product.brand or "",
            "model": product.model or "",
            "price": str(from_minor_units(price_minor)),
            "quantity": reference.quantity,
            "image_url": product.image_url or "",
            "specs": deepcopy(product.specs or {}),
        })

    compatibility = evaluate_diy_compatibility(
        products_by_slot,
        configuration_id=configuration.id,
        configuration_version=configuration.version,
    )
    if compatibility.blocked:
        issue_summary = "; ".join(
            f"{issue.rule_id}: {issue.remediation}"
            for issue in compatibility.issues
        )
        raise OrderCreationError(
            409,
            f"DIY configuration is blocked by compatibility checks: {issue_summary}",
            payload={
                "code": "DIY_COMPATIBILITY_BLOCKED",
                "compatibility": compatibility.as_payload(),
            },
        )

    unit_price_minor = parts_total_minor + variant.surcharge_minor + material.surcharge_minor
    appearance_surcharge_minor = variant.surcharge_minor + material.surcharge_minor
    snapshot = {
        "type": "diy_pc",
        "configuration_id": configuration.id,
        "version": configuration.version,
        "created_at": created_at.isoformat(),
        "parts": parts,
        "appearance": {
            "variant_id": variant.id,
            "variant_name": variant.name,
            "material_id": material.id,
            "material_name": material.name,
            "price_diff": str(from_minor_units(appearance_surcharge_minor)),
        },
        "pricing": {
            "parts_total": str(from_minor_units(parts_total_minor)),
            "appearance_price_diff": str(from_minor_units(appearance_surcharge_minor)),
            "total": str(from_minor_units(unit_price_minor)),
        },
        "compatibility_rules_version": compatibility.rules.version,
        "compatibility_status": compatibility.status,
    }
    snapshot["metrics"] = {
        "total_power_w": compatibility.total_power_w,
        "psu_headroom_w": compatibility.psu_headroom_w,
        "gpu_space_headroom_mm": compatibility.gpu_space_headroom_mm,
        "compatibility_rules_version": compatibility.rules.version,
        "compatibility_status": compatibility.status,
        # Preserve the existing frontend key/title/level/message fields;
        # server-owned rule_id/status/remediation/parts are additive.
        "compatibility": compatibility.checks_as_dicts(),
    }
    specs: dict[str, Any] = {
        "custom_type": "diy_pc",
        "\u914d\u7f6e\u7c7b\u578b": "DIY \u88c5\u673a\u6574\u673a",
        "3D \u5916\u89c2": f"{variant.name} / {material.name}",
        "_snapshot": snapshot,
    }
    for part in parts:
        specs[part["label"]] = f"{part['brand']} {part['name']}".strip()

    return PricedOrderItem(
        item_type="custom",
        product_id=None,
        product_name=configuration.name,
        product_image=image_by_slot.get("case") or image_by_slot.get("gpu"),
        product_specs=specs,
        price_minor=unit_price_minor,
        quantity=item.quantity,
        subtotal_minor=unit_price_minor * item.quantity,
        configuration_id=configuration.id,
        configuration_version=configuration.version,
    )


def price_order_sources(
    cart_items: Sequence[CartItem],
    custom_items: Sequence[CustomOrderItemCreate],
    products: Mapping[UUID, Product],
    *,
    created_at: datetime | None = None,
) -> PricedOrder:
    """Validate sources and return immutable, server-built pricing snapshots."""
    snapshot_time = created_at or datetime.now(timezone.utc)
    inventory: defaultdict[UUID, int] = defaultdict(int)
    priced_items: list[PricedOrderItem] = []
    custom_sources: list[tuple[CustomOrderItemCreate, DiyConfiguration]] = []

    for cart_item in cart_items:
        product = products.get(cart_item.product_id)
        if product is None:
            raise OrderCreationError(400, f"Product {cart_item.product_id} does not exist")
        inventory[product.id] += cart_item.quantity
        price_minor = to_minor_units(product.price)
        priced_items.append(PricedOrderItem(
            item_type="product",
            product_id=product.id,
            product_name=product.name,
            product_image=product.image_url,
            product_specs=deepcopy(product.specs or {}),
            price_minor=price_minor,
            quantity=cart_item.quantity,
            subtotal_minor=price_minor * cart_item.quantity,
        ))

    for custom_item in custom_items:
        configuration = get_diy_configuration(
            custom_item.configuration.configuration_id,
            custom_item.configuration.version,
        )
        if configuration is None:
            raise OrderCreationError(409, "DIY configuration version is unsupported; refresh the builder")
        for reference in custom_item.configuration.parts:
            inventory[reference.product_id] += reference.quantity * custom_item.quantity
        custom_sources.append((custom_item, configuration))

    for product_id, required_quantity in inventory.items():
        product = products.get(product_id)
        if product is None:
            raise OrderCreationError(400, f"Product {product_id} does not exist")
        _validate_product_available(product, required_quantity)

    # Run compatibility checks only after availability checks so the caller
    # receives the most immediate actionable order error when a selected part
    # has gone out of stock or has been delisted.
    for custom_item, configuration in custom_sources:
        priced_items.append(_diy_snapshot(custom_item, configuration, products, snapshot_time))

    return PricedOrder(
        items=tuple(priced_items),
        inventory=dict(inventory),
        total_minor=sum(item.subtotal_minor for item in priced_items),
    )


def calculate_shipping_minor(total_minor: int) -> int:
    if total_minor >= to_minor_units(settings.FREE_SHIPPING_THRESHOLD):
        return 0
    return to_minor_units(settings.SHIPPING_FEE)


def _request_fingerprint(order_data: OrderCreate) -> str:
    payload = order_data.model_dump(mode="json", exclude={"idempotency_key"})
    payload["cart_item_ids"] = sorted(payload["cart_item_ids"] or []) if payload["cart_item_ids"] is not None else None
    for custom_item in payload.get("custom_items") or []:
        custom_item["configuration"]["parts"] = sorted(
            custom_item["configuration"]["parts"],
            key=lambda part: (part["slot_id"], part["product_id"], part["quantity"]),
        )
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(canonical.encode("utf-8")).hexdigest()


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order_data: OrderCreate, user_id: UUID) -> Order:
        idempotency_key = order_data.idempotency_key or uuid4()
        fingerprint = _request_fingerprint(order_data)

        existing = await self._find_existing_order(user_id, idempotency_key)
        if existing is not None:
            return self._validate_idempotent_replay(existing, fingerprint)

        try:
            address = await self._get_address(user_id, order_data.address_id)
            if address is None:
                raise OrderCreationError(404, "Shipping address does not exist")

            cart_items = await self._get_cart_items(user_id, order_data.cart_item_ids)
            custom_items = order_data.custom_items or []
            # A concurrent request with the same idempotency key may have
            # committed while this request was waiting on the cart/product
            # reads. Re-check before treating a now-empty cart as a new
            # request.
            existing = await self._find_existing_order(user_id, idempotency_key)
            if existing is not None:
                return self._validate_idempotent_replay(existing, fingerprint)
            if not cart_items and not custom_items:
                raise OrderCreationError(400, "Cart is empty")
            if order_data.cart_item_ids is not None and len(cart_items) != len(set(order_data.cart_item_ids)):
                raise OrderCreationError(400, "One or more cart items do not exist")

            product_ids = {item.product_id for item in cart_items}
            product_ids.update(
                reference.product_id
                for custom_item in custom_items
                for reference in custom_item.configuration.parts
            )
            products = await self._lock_products(product_ids)
            # The first idempotency lookup is intentionally non-locking. Once
            # the inventory rows are locked, a request that raced with the
            # creator must replay the committed order instead of re-pricing
            # against its now-depleted stock.
            existing = await self._find_existing_order(user_id, idempotency_key)
            if existing is not None:
                return self._validate_idempotent_replay(existing, fingerprint)
            priced = price_order_sources(cart_items, custom_items, products)
            shipping_minor = calculate_shipping_minor(priced.total_minor)

            order = Order(
                id=uuid4(),
                order_no=self._generate_order_no(),
                user_id=user_id,
                status="pending",
                idempotency_key=idempotency_key,
                request_fingerprint=fingerprint,
                total_amount=from_minor_units(priced.total_minor),
                shipping_fee=from_minor_units(shipping_minor),
                discount_amount=from_minor_units(0),
                final_amount=from_minor_units(priced.total_minor + shipping_minor),
                recipient_name=address.recipient_name,
                recipient_phone=address.phone,
                shipping_address=f"{address.province}{address.city}{address.district}{address.address}",
                remark=order_data.remark,
            )
            self.db.add(order)

            for item in priced.items:
                self.db.add(OrderItem(
                    id=uuid4(),
                    order_id=order.id,
                    product_id=item.product_id,
                    item_type=item.item_type,
                    product_name=item.product_name,
                    product_image=item.product_image,
                    product_specs=deepcopy(item.product_specs),
                    configuration_id=item.configuration_id,
                    configuration_version=item.configuration_version,
                    price=from_minor_units(item.price_minor),
                    quantity=item.quantity,
                    subtotal=from_minor_units(item.subtotal_minor),
                ))

            for product_id, quantity in priced.inventory.items():
                product = products[product_id]
                product.stock -= quantity
                product.sold_count = (product.sold_count or 0) + quantity

            for cart_item in cart_items:
                await self.db.delete(cart_item)

            await self.db.flush()
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            existing = await self._find_existing_order(user_id, idempotency_key)
            if existing is not None:
                return self._validate_idempotent_replay(existing, fingerprint)
            raise
        except Exception:
            await self.db.rollback()
            raise

        return await self._load_order(order.id)

    @staticmethod
    def _validate_idempotent_replay(order: Order, fingerprint: str) -> Order:
        if order.request_fingerprint != fingerprint:
            raise OrderCreationError(409, "Idempotency key was already used for a different order request")
        return order

    async def _find_existing_order(self, user_id: UUID, idempotency_key: UUID) -> Order | None:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id, Order.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def _get_address(self, user_id: UUID, address_id: UUID) -> UserAddress | None:
        result = await self.db.execute(
            select(UserAddress).where(UserAddress.id == address_id, UserAddress.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_cart_items(self, user_id: UUID, cart_item_ids: Sequence[UUID] | None) -> list[CartItem]:
        query = select(CartItem).where(CartItem.user_id == user_id)
        if cart_item_ids is not None:
            query = query.where(CartItem.id.in_(cart_item_ids))
        result = await self.db.execute(query.order_by(CartItem.id))
        return list(result.scalars().all())

    async def _lock_products(self, product_ids: Iterable[UUID]) -> dict[UUID, Product]:
        ordered_ids = sorted(set(product_ids), key=str)
        if not ordered_ids:
            return {}
        result = await self.db.execute(
            select(Product)
            .where(Product.id.in_(ordered_ids))
            .order_by(Product.id)
            .with_for_update()
        )
        return {product.id: product for product in result.scalars().all()}

    async def _load_order(self, order_id: UUID) -> Order:
        result = await self.db.execute(
            select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        )
        return result.scalar_one()

    @staticmethod
    def _generate_order_no() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"PC{timestamp}{uuid4().hex[:8].upper()}"


def inventory_from_order_items(items: Sequence[OrderItem]) -> dict[UUID, int]:
    """Return stock quantities represented by normal and DIY snapshots."""
    inventory: defaultdict[UUID, int] = defaultdict(int)
    for item in items:
        if item.product_id:
            inventory[item.product_id] += item.quantity
            continue
        snapshot = (item.product_specs or {}).get("_snapshot", {})
        if snapshot.get("type") != "diy_pc":
            continue
        for part in snapshot.get("parts", []):
            try:
                inventory[UUID(str(part["product_id"]))] += int(part.get("quantity", 1)) * item.quantity
            except (KeyError, TypeError, ValueError):
                continue
    return dict(inventory)
