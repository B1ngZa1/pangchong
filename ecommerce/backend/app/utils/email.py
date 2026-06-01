"""
胖虫电商系统 - 邮件发送工具
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    发送邮件

    Args:
        to_email: 收件人邮箱
        subject: 邮件主题
        html_content: HTML 内容
        text_content: 纯文本内容（可选）

    Returns:
        bool: 是否发送成功
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP 未配置，跳过邮件发送")
        return False

    # 创建邮件
    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject

    # 添加纯文本内容
    if text_content:
        message.attach(MIMEText(text_content, "plain", "utf-8"))

    # 添加 HTML 内容
    message.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        # 发送邮件
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True
        )
        logger.info(f"邮件发送成功: {to_email}")
        return True
    except Exception as e:
        logger.error(f"邮件发送失败: {to_email}, 错误: {str(e)}")
        return False


async def send_order_confirmation_email(
    to_email: str,
    order_no: str,
    order_amount: float,
    items: list
) -> bool:
    """
    发送订单确认邮件

    Args:
        to_email: 收件人邮箱
        order_no: 订单号
        order_amount: 订单金额
        items: 订单商品列表

    Returns:
        bool: 是否发送成功
    """
    # 构建商品列表 HTML
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['product_name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">¥{item['price']:.2f}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">¥{item['subtotal']:.2f}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Noto Sans SC', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #44D62C; color: #000; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #fff; padding: 20px; border: 1px solid #eee; }}
            .footer {{ background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #f5f5f5; padding: 10px; text-align: left; }}
            .total {{ font-size: 18px; font-weight: bold; color: #44D62C; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>订单确认</h1>
            </div>
            <div class="content">
                <p>尊敬的用户，您好！</p>
                <p>您的订单已成功提交，订单号：<strong>{order_no}</strong></p>

                <h3>订单详情</h3>
                <table>
                    <thead>
                        <tr>
                            <th>商品名称</th>
                            <th style="text-align: center;">数量</th>
                            <th style="text-align: right;">单价</th>
                            <th style="text-align: right;">小计</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>

                <p style="text-align: right; margin-top: 20px;">
                    订单总额：<span class="total">¥{order_amount:.2f}</span>
                </p>

                <p>我们将尽快为您处理订单，如有任何问题，请联系客服。</p>
            </div>
            <div class="footer">
                <p>胖虫科技 - 极致性能，由你定义</p>
                <p>客服邮箱：support@pangchong.com</p>
            </div>
        </div>
    </body>
    </html>
    """

    return await send_email(
        to_email=to_email,
        subject=f"订单确认 - {order_no}",
        html_content=html_content
    )


async def send_welcome_email(to_email: str, username: str) -> bool:
    """
    发送欢迎邮件

    Args:
        to_email: 收件人邮箱
        username: 用户名

    Returns:
        bool: 是否发送成功
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Noto Sans SC', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #44D62C; color: #000; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #fff; padding: 20px; border: 1px solid #eee; }}
            .footer {{ background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
            .btn {{ display: inline-block; background: #44D62C; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>欢迎加入胖虫科技！</h1>
            </div>
            <div class="content">
                <p>亲爱的 {username}，您好！</p>
                <p>感谢您注册成为胖虫科技的用户！</p>
                <p>我们致力于为每一位DIY爱好者提供极致性能的电脑产品。</p>

                <h3>您可以：</h3>
                <ul>
                    <li>浏览我们的全系列产品</li>
                    <li>使用在线装机工具自定义配置</li>
                    <li>享受专业的售前售后服务</li>
                </ul>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000" class="btn">开始购物</a>
                </p>
            </div>
            <div class="footer">
                <p>胖虫科技 - 极致性能，由你定义</p>
                <p>客服邮箱：support@pangchong.com</p>
            </div>
        </div>
    </body>
    </html>
    """

    return await send_email(
        to_email=to_email,
        subject="欢迎加入胖虫科技！",
        html_content=html_content
    )
