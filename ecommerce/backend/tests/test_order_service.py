"""BE-101..103 security and lifecycle tests for authoritative order creation."""
from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import CustomOrderItemCreate, OrderCreate
from app.services.diy_catalog import DIY_CONFIGURATION
from app.services.money import from_minor_units
from app.services.orders import OrderCreationError, OrderService, price_order_sources


USER_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
ADDRESS_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def make_product(*, category_id=None, price="10.00", stock=10, active=True, name="Part"):
    return Product(
        id=uuid4(),
        name=name,
        slug=f"part-{uuid4()}",
        category_id=category_id,
        price=Decimal(price),
        stock=stock,
        sold_count=0,
        is_active=active,
        specs={"source": "server"},
    )


def make_diy_products(*, price="10.00", stock=10, active=True):
    products = {}
    specs_by_slot = {
        "cpu": {"socket": "AM5", "tdp": "65W"},
        "gpu": {"length": "300mm", "tdp": "100W"},
        "motherboard": {"socket": "AM5", "form_factor": "ATX", "memory": "DDR5 x4"},
        "ram": {"type": "DDR5"},
        "ssd": {},
        "cooler": {"type": "风冷单塔", "height": "155mm", "tdp_support": "150W"},
        "psu": {"wattage": "850W"},
        "case": {"mb_support": "ATX", "gpu_length": "400mm", "cooler_height": "175mm"},
    }
    for slot in DIY_CONFIGURATION.slots.values():
        product = make_product(
            category_id=slot.category_id,
            price=price,
            stock=stock,
            active=active,
            name=f"Server {slot.id}",
        )
        product.specs.update(specs_by_slot[slot.id])
        products[product.id] = product
    return products


def make_diy_item(products, *, quantity=1, variant_id="black"):
    by_category = {product.category_id: product for product in products.values()}
    return CustomOrderItemCreate.model_validate({
        "configuration": {
            "configuration_id": DIY_CONFIGURATION.id,
            "version": DIY_CONFIGURATION.version,
            "variant_id": variant_id,
            "material_id": "matte",
            "parts": [
                {
                    "slot_id": slot.id,
                    "product_id": by_category[slot.category_id].id,
                    "quantity": 1,
                }
                for slot in DIY_CONFIGURATION.slots.values()
            ],
        },
        "quantity": quantity,
    })


def make_cart_item(product, quantity=1):
    return CartItem(id=uuid4(), user_id=USER_ID, product_id=product.id, quantity=quantity)


def test_client_supplied_one_cent_prices_are_not_part_of_either_contract():
    with pytest.raises(ValidationError):
        OrderCreate.model_validate({
            "address_id": str(ADDRESS_ID),
            "cart_item_ids": [str(uuid4())],
            "price": "0.01",
        })

    products = make_diy_products()
    valid_item = make_diy_item(products).model_dump(mode="json")
    valid_item["price"] = "0.01"
    with pytest.raises(ValidationError):
        CustomOrderItemCreate.model_validate(valid_item)


def test_normal_and_diy_totals_use_decimal_minor_units_and_server_prices():
    normal = make_product(price="0.10", stock=3, name="Server GPU")
    diy_products = make_diy_products(price="0.10", stock=2)
    products = {normal.id: normal, **diy_products}

    priced = price_order_sources(
        [make_cart_item(normal, quantity=3)],
        [make_diy_item(diy_products, quantity=2, variant_id="green")],
        products,
    )

    # 3 * 0.10 + 2 * (8 * 0.10 + 500.00), exactly in cents.
    assert from_minor_units(priced.total_minor) == Decimal("1001.90")
    assert from_minor_units(priced.items[0].price_minor) == Decimal("0.10")
    assert from_minor_units(priced.items[1].price_minor) == Decimal("500.80")


@pytest.mark.parametrize("source", ["normal", "diy"])
def test_out_of_stock_is_rejected_for_normal_and_diy_sources(source):
    if source == "normal":
        product = make_product(stock=0)
        cart_items, custom_items, products = [make_cart_item(product)], [], {product.id: product}
    else:
        products = make_diy_products()
        next(iter(products.values())).stock = 0
        cart_items, custom_items = [], [make_diy_item(products)]

    with pytest.raises(OrderCreationError, match="out of stock"):
        price_order_sources(cart_items, custom_items, products)


@pytest.mark.parametrize("source", ["normal", "diy"])
def test_delisted_is_rejected_for_normal_and_diy_sources(source):
    if source == "normal":
        product = make_product(active=False)
        cart_items, custom_items, products = [make_cart_item(product)], [], {product.id: product}
    else:
        products = make_diy_products()
        next(iter(products.values())).is_active = False
        cart_items, custom_items = [], [make_diy_item(products)]

    with pytest.raises(OrderCreationError, match="delisted"):
        price_order_sources(cart_items, custom_items, products)


def test_changed_prices_are_recomputed_and_persisted_snapshots_do_not_follow_catalog_mutations():
    normal = make_product(price="19.99", name="Current normal name")
    diy_products = make_diy_products(price="2.50")
    priced = price_order_sources(
        [make_cart_item(normal, quantity=2)],
        [make_diy_item(diy_products)],
        {normal.id: normal, **diy_products},
    )

    normal_snapshot = priced.items[0]
    diy_snapshot = priced.items[1].product_specs["_snapshot"]
    assert from_minor_units(normal_snapshot.subtotal_minor) == Decimal("39.98")
    assert diy_snapshot["pricing"]["parts_total"] == "20.00"

    normal.price = Decimal("0.01")
    normal.name = "Mutated catalog name"
    first_diy_product = next(iter(diy_products.values()))
    first_diy_product.price = Decimal("0.01")
    first_diy_product.specs["source"] = "mutated"

    assert normal_snapshot.product_name == "Current normal name"
    assert from_minor_units(normal_snapshot.price_minor) == Decimal("19.99")
    assert diy_snapshot["pricing"]["parts_total"] == "20.00"
    assert diy_snapshot["parts"][0]["specs"] == {
        "source": "server",
        "socket": "AM5",
        "tdp": "65W",
    }


class MemoryDb:
    def __init__(self):
        self.orders = {}
        self.orders_by_id = {}
        self.deleted = []
        self.commit_count = 0
        self.rollback_count = 0

    def add(self, value):
        if isinstance(value, Order):
            self.orders[(value.user_id, value.idempotency_key)] = value
            self.orders_by_id[value.id] = value
        elif isinstance(value, OrderItem):
            self.orders_by_id[value.order_id].items.append(value)

    async def delete(self, value):
        self.deleted.append(value)

    async def flush(self):
        return None

    async def commit(self):
        self.commit_count += 1

    async def rollback(self):
        self.rollback_count += 1


class MemoryOrderService(OrderService):
    def __init__(self, db, *, address, cart_items, products):
        super().__init__(db)
        self.address = address
        self.cart_items = cart_items
        self.products = products

    async def _find_existing_order(self, user_id, idempotency_key):
        return self.db.orders.get((user_id, idempotency_key))

    async def _get_address(self, user_id, address_id):
        return self.address if address_id == ADDRESS_ID else None

    async def _get_cart_items(self, user_id, cart_item_ids):
        return self.cart_items

    async def _lock_products(self, product_ids):
        return self.products

    async def _load_order(self, order_id):
        return self.db.orders_by_id[order_id]


@pytest.mark.asyncio
async def test_duplicate_submit_returns_the_original_order_and_decrements_stock_once():
    product = make_product(price="25.00", stock=2)
    cart_item = make_cart_item(product)
    database = MemoryDb()
    service = MemoryOrderService(
        database,
        address=SimpleNamespace(
            recipient_name="Buyer",
            phone="13800000000",
            province="Shanghai",
            city="Shanghai",
            district="Pudong",
            address="Test Road 1",
        ),
        cart_items=[cart_item],
        products={product.id: product},
    )
    key = uuid4()
    request = OrderCreate(
        address_id=ADDRESS_ID,
        cart_item_ids=[cart_item.id],
        custom_items=[],
        idempotency_key=key,
    )

    first = await service.create_order(request, USER_ID)
    replay = await service.create_order(request, USER_ID)

    assert replay.id == first.id
    assert len(database.orders) == 1
    assert database.commit_count == 1
    assert product.stock == 1
    assert product.sold_count == 1

    conflicting_request = OrderCreate(
        address_id=ADDRESS_ID,
        cart_item_ids=[cart_item.id],
        custom_items=[],
        remark="different payload",
        idempotency_key=key,
    )
    with pytest.raises(OrderCreationError) as exc_info:
        await service.create_order(conflicting_request, USER_ID)
    assert exc_info.value.status_code == 409
    assert product.stock == 1
