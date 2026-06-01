"""
胖虫电商系统 - Schema 包
"""
from .user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
    UserBase,
    UserResponse,
    UserUpdate,
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)
from .product import (
    CategoryBase,
    CategoryCreate,
    CategoryResponse,
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductBrief,
)
from .cart import (
    CartItemAdd,
    CartItemUpdate,
    CartItemResponse,
    CartResponse,
    CartMergeRequest,
)
from .order import (
    OrderStatus,
    CustomOrderItemCreate,
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    OrderListResponse,
    OrderPayRequest,
    OrderShipRequest,
    OrderCancelRequest,
)

__all__ = [
    # User
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "TokenRefresh",
    "PasswordChange",
    "UserBase",
    "UserResponse",
    "UserUpdate",
    "AddressCreate",
    "AddressUpdate",
    "AddressResponse",
    # Product
    "CategoryBase",
    "CategoryCreate",
    "CategoryResponse",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    "ProductBrief",
    # Cart
    "CartItemAdd",
    "CartItemUpdate",
    "CartItemResponse",
    "CartResponse",
    "CartMergeRequest",
    # Order
    "OrderStatus",
    "CustomOrderItemCreate",
    "OrderCreate",
    "OrderItemResponse",
    "OrderResponse",
    "OrderListResponse",
    "OrderPayRequest",
    "OrderShipRequest",
    "OrderCancelRequest",
]
