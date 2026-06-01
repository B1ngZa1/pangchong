"""
胖虫电商系统 - 支付 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_current_user
from ..core.config import settings
from ..models.user import User
from ..models.order import Order, OrderItem
from ..schemas.order import OrderPayRequest, OrderResponse

router = APIRouter(prefix="/payment", tags=["支付"])


# ============ 支付宝集成 ============

class AlipayService:
    """支付宝服务（沙箱环境）"""

    def __init__(self):
        self.app_id = settings.ALIPAY_APP_ID
        self.private_key = settings.ALIPAY_PRIVATE_KEY
        self.public_key = settings.ALIPAY_PUBLIC_KEY
        self.gateway = settings.ALIPAY_GATEWAY
        self.sandbox = settings.ALIPAY_SANDBOX

    def create_payment_url(self, order_no: str, amount: float, subject: str) -> str:
        """
        创建支付链接（沙箱环境模拟）

        实际生产环境需要：
        1. 使用支付宝 SDK
        2. RSA2 签名
        3. 调用 alipay.trade.page.pay 接口
        """
        if self.sandbox:
            # 沙箱环境返回模拟链接
            return f"https://openapi.alipay.com/gateway.do?mock_pay=true&order_no={order_no}&amount={amount}"

        # 生产环境实现（需要安装 alipay-sdk-python）
        # from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
        # from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
        # from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
        # from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest

        # alipay_config = AlipayClientConfig()
        # alipay_config.server_url = self.gateway
        # alipay_config.app_id = self.app_id
        # alipay_config.app_private_key = self.private_key
        # alipay_config.alipay_public_key = self.public_key

        # client = DefaultAlipayClient(alipay_client_config=alipay_config)
        # model = AlipayTradePagePayModel()
        # model.out_trade_no = order_no
        # model.total_amount = str(amount)
        # model.subject = subject
        # model.product_code = "FAST_INSTANT_TRADE_PAY"

        # request = AlipayTradePagePayRequest(biz_model=model)
        # response = client.page_execute(request, http_method="GET")
        # return response

        return f"{self.gateway}?order_no={order_no}&amount={amount}"

    def verify_callback(self, params: dict) -> bool:
        """
        验证支付回调签名

        生产环境需要配置支付宝 SDK 进行 RSA2 验签。
        沙箱环境跳过验签但仍校验 app_id。
        """
        if self.sandbox:
            # 沙箱环境：校验 app_id 是否匹配（防止外部伪造）
            callback_app_id = params.get("app_id")
            if callback_app_id and self.app_id and callback_app_id != self.app_id:
                return False
            return True

        # 生产环境：必须配置密钥
        if not self.public_key:
            return False

        # 生产环境实现（需要安装 alipay-sdk-python）
        # from alipay.aop.api.util.SignatureUtils import verify_with_rsa
        # sign = params.pop("sign", "")
        # sign_type = params.pop("sign_type", "")
        # ordered_params = sorted(params.items())
        # sign_str = "&".join([f"{k}={v}" for k, v in ordered_params])
        # return verify_with_rsa(self.public_key, sign_str, sign)

        # 未配置 SDK 时拒绝回调
        return False


alipay_service = AlipayService()


# ============ 创建支付 ============

@router.post("/create/{order_id}")
async def create_payment(
    order_id: UUID,
    pay_data: OrderPayRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建支付订单

    - **payment_method**: 支付方式（alipay/wechat）
    """
    # 查询订单
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不允许支付"
        )

    # 更新支付方式
    order.payment_method = pay_data.payment_method
    await db.flush()

    # 创建支付链接
    if pay_data.payment_method == "alipay":
        # 获取订单商品信息作为支付描述
        items_result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        items = items_result.scalars().all()
        subject = f"胖虫科技-{items[0].product_name}" if items else "胖虫科技订单"

        payment_url = alipay_service.create_payment_url(
            order_no=order.order_no,
            amount=float(order.final_amount),
            subject=subject
        )

        return {
            "payment_url": payment_url,
            "order_no": order.order_no,
            "amount": float(order.final_amount)
        }
    elif pay_data.payment_method == "wechat":
        # 微信支付实现（需要安装 wechatpay-python）
        # from wechatpay import WeChatPay
        # wxpay = WeChatPay(...)
        # result = wxpay.pay(...)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="微信支付暂未实现"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的支付方式"
        )


# ============ 支付回调 ============

@router.post("/callback/alipay")
async def alipay_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """
    支付宝支付回调通知

    支付宝会 POST 请求此接口，携带支付结果参数
    """
    # 获取回调参数
    form_data = await request.form()
    params = dict(form_data)

    # 验证签名
    if not alipay_service.verify_callback(params):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="签名验证失败"
        )

    # 获取关键参数
    order_no = params.get("out_trade_no")
    trade_no = params.get("trade_no")  # 支付宝交易号
    trade_status = params.get("trade_status")
    total_amount = params.get("total_amount")

    if not order_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少订单号"
        )

    # 查询订单
    result = await db.execute(select(Order).where(Order.order_no == order_no))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 防止重复支付
    if order.is_paid:
        return {"success": True, "message": "订单已支付"}

    # 验证金额
    if not total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少金额参数"
        )
    try:
        amount_value = float(total_amount)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="金额格式无效"
        )
    if amount_value != float(order.final_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="金额不匹配"
        )

    # 处理支付结果
    if trade_status == "TRADE_SUCCESS" or trade_status == "TRADE_FINISHED":
        order.status = "paid"
        order.payment_id = trade_no
        order.paid_at = datetime.utcnow()
        await db.flush()

    return {"success": True, "message": "支付成功"}


# ============ 模拟支付（沙箱环境） ============

@router.post("/sandbox/mock-pay/{order_id}", response_model=OrderResponse)
async def sandbox_mock_pay(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    模拟支付（仅用于沙箱测试）

    跳过实际支付流程，直接将订单标记为已支付
    仅在 ALIPAY_SANDBOX=True 时可用
    """
    if not settings.ALIPAY_SANDBOX:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不允许支付"
        )

    # 模拟支付成功
    order.status = "paid"
    order.payment_id = f"MOCK_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    order.paid_at = datetime.utcnow()

    await db.flush()
    return order


# ============ 查询支付状态 ============

@router.get("/status/{order_no}")
async def get_payment_status(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """查询支付状态"""
    result = await db.execute(
        select(Order).where(
            Order.order_no == order_no,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    return {
        "order_no": order.order_no,
        "status": order.status,
        "is_paid": order.is_paid,
        "paid_at": order.paid_at,
        "payment_id": order.payment_id
    }
