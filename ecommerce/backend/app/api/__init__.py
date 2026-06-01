"""
胖虫电商系统 - API 路由包
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .products import router as products_router
from .cart import router as cart_router
from .orders import router as orders_router
from .payment import router as payment_router
from .admin import router as admin_router
from .market import router as market_router

# 创建主路由
api_router = APIRouter(prefix="/api")

# 注册子路由
api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(payment_router)
api_router.include_router(admin_router)
api_router.include_router(market_router)

__all__ = ["api_router"]
