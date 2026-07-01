"""
胖虫电商系统 - 核心配置
"""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # 应用基本信息
    APP_NAME: str = "胖虫电商系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://pangchong:CHANGE_ME@localhost:5432/pangchong_ecommerce"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 配置
    SECRET_KEY: str = "CHANGE_THIS_TO_A_RANDOM_SECRET_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 安全配置
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    CSRF_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS 配置
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # 支付宝配置
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""
    ALIPAY_GATEWAY: str = "https://openapi.alipay.com/gateway.do"
    ALIPAY_SANDBOX: bool = True

    # 邮件配置
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@pangchong.com"
    SMTP_FROM_NAME: str = "胖虫科技"

    # 快递鸟配置
    KDNIAO_APP_KEY: str = ""
    KDNIAO_APP_SECRET: str = ""

    # 商品价格走势 API（推荐接 TMAPI，覆盖淘宝/天猫/京东/拼多多历史价格）
    PRICE_HISTORY_PROVIDER: str = "tmapi"
    PRICE_HISTORY_API_BASE_URL: str = "https://api.tmapi.top/price-comparison/historical-price-cn/get-item-historical-price-by-id"
    PRICE_HISTORY_API_KEY: str = ""
    PRICE_HISTORY_TIMEOUT_SECONDS: float = 6.0

    # Supabase 仅作为托管 Postgres 与 Storage；密钥只能存在于后端。
    SUPABASE_URL: str = ""
    SUPABASE_SECRET_KEY: str = ""
    SUPABASE_IMAGE_BUCKET: str = "catalog-images"
    SUPABASE_MODEL_BUCKET: str = "catalog-models"

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 运费规则
    FREE_SHIPPING_THRESHOLD: float = 299.0  # 满299包邮
    SHIPPING_FEE: float = 10.0  # 固定运费10元


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
