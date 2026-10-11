"""
胖虫电商系统 - 核心配置
"""
from __future__ import annotations

from pydantic import ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings
from typing import Literal
from urllib.parse import unquote, urlsplit


_PLACEHOLDER_MARKERS = (
    "change-me",
    "change_this",
    "changethis",
    "replace-me",
    "replace_this",
    "placeholder",
    "your-secret",
    "local-dev",
)

_KNOWN_WEAK_CREDENTIALS = {
    "123456",
    "admin",
    "password",
    "postgres",
    "redis",
    "secret",
    "test",
    "test123456",
    "pangchong_dev_password",
    "pangchong_dev_redis",
}

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or any(marker in normalized for marker in _PLACEHOLDER_MARKERS)


def _is_weak_secret_key(value: str) -> bool:
    secret = value.strip()
    return (
        _is_placeholder(secret)
        or len(secret) < 32
        or len(set(secret)) < 8
    )


def _is_weak_service_password(value: str, *, username: str | None = None) -> bool:
    """Apply the production password floor to database/cache credentials."""
    password = value.strip()
    normalized = password.casefold()
    return (
        _is_placeholder(password)
        or normalized in _KNOWN_WEAK_CREDENTIALS
        or (username is not None and normalized == username.strip().casefold())
        or len(password) < 16
        or len(set(password)) < 6
    )


def _service_url_error(
    value: str,
    *,
    field_name: str,
    allowed_schemes: tuple[str, ...],
) -> str | None:
    """Return a safe error without ever including the credential-bearing URL."""
    try:
        parsed = urlsplit(value)
        password = unquote(parsed.password or "")
        username = unquote(parsed.username or "")
    except ValueError:
        return f"{field_name} must be a valid credential-bearing URL"

    if parsed.scheme not in allowed_schemes or not parsed.hostname:
        return f"{field_name} must use an approved scheme and include a host"
    if not password:
        return f"{field_name} must include a password"
    if _is_weak_service_password(password, username=username):
        return (
            f"{field_name} password must be non-default, at least 16 characters, "
            "and contain at least 6 distinct characters"
        )
    return None


def _cors_origin_error(origin: str) -> str | None:
    if origin == "*":
        return "ALLOWED_ORIGINS must not contain a wildcard"

    try:
        parsed = urlsplit(origin)
    except ValueError:
        return "ALLOWED_ORIGINS entries must be valid HTTPS origins"

    hostname = (parsed.hostname or "").casefold()
    if parsed.scheme != "https" or not hostname:
        return "ALLOWED_ORIGINS entries must use HTTPS"
    if hostname in _LOCAL_HOSTS or hostname.endswith(".localhost"):
        return "ALLOWED_ORIGINS must not contain local hosts in production"
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return "ALLOWED_ORIGINS entries must be origins without credentials or query data"
    if parsed.path not in ("", "/"):
        return "ALLOWED_ORIGINS entries must not contain a path"
    return None


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
    APP_ENV: Literal["development", "test", "staging", "production"] = "development"
    DEBUG: bool = False
    RELOAD: bool = False
    WEB_CONCURRENCY: int = Field(default=1, ge=1, le=16)

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://pangchong:pangchong_dev_password@localhost:5432/pangchong_ecommerce"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 配置
    SECRET_KEY: str = "CHANGE_THIS_TO_A_RANDOM_SECRET_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AUTH_REFRESH_COOKIE_NAME: str = "pangchong_refresh"
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # 安全配置
    # 20 MB GLB plus multipart framing; per-file limits are enforced by the route.
    MAX_REQUEST_SIZE: int = 22 * 1024 * 1024
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    CSRF_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS 配置
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # 支付宝配置
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""
    ALIPAY_GATEWAY: str = "https://openapi.alipay.com/gateway.do"
    ALIPAY_SANDBOX: bool = True
    ALIPAY_NOTIFY_URL: str = ""
    ALIPAY_RETURN_URL: str = ""
    ALIPAY_SELLER_ID: str = ""

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
    ASSET_STORAGE_BACKEND: Literal["local", "supabase"] = "local"

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 运费规则
    FREE_SHIPPING_THRESHOLD: float = 299.0  # 满299包邮
    SHIPPING_FEE: float = 10.0  # 固定运费10元

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        """Reject development credentials and process modes in production."""
        if self.APP_ENV != "production":
            return self

        errors: list[str] = []
        if _is_weak_secret_key(self.SECRET_KEY):
            errors.append(
                "SECRET_KEY must be non-placeholder, at least 32 characters, "
                "and contain at least 8 distinct characters"
            )

        for field_name, allowed_schemes in (
            ("DATABASE_URL", ("postgresql", "postgresql+asyncpg")),
            ("REDIS_URL", ("redis", "rediss")),
        ):
            if error := _service_url_error(
                getattr(self, field_name),
                field_name=field_name,
                allowed_schemes=allowed_schemes,
            ):
                errors.append(error)

        if self.DEBUG:
            errors.append("DEBUG must be false")
        if self.RELOAD:
            errors.append("RELOAD must be false")
        if self.AUTH_COOKIE_SAMESITE == "none" and not self.AUTH_COOKIE_SECURE:
            errors.append("AUTH_COOKIE_SECURE must be true when AUTH_COOKIE_SAMESITE is none")
        if not self.AUTH_COOKIE_SECURE:
            errors.append("AUTH_COOKIE_SECURE must be true")
        if self.ALIPAY_SANDBOX:
            errors.append("ALIPAY_SANDBOX must be false")

        if not self.ALLOWED_ORIGINS:
            errors.append("ALLOWED_ORIGINS must contain at least one production origin")
        else:
            for origin in self.ALLOWED_ORIGINS:
                if error := _cors_origin_error(origin):
                    errors.append(error)

        if _is_placeholder(self.ALIPAY_APP_ID):
            errors.append("ALIPAY_APP_ID is required and must not be a placeholder")
        for field_name in ("ALIPAY_PRIVATE_KEY", "ALIPAY_PUBLIC_KEY"):
            value = getattr(self, field_name)
            if _is_placeholder(value) or len(value.strip()) < 16:
                errors.append(
                    f"{field_name} is required, must not be a placeholder, "
                    "and must contain at least 16 characters"
                )

        if errors:
            raise ValueError("Unsafe production configuration: " + "; ".join(errors))

        return self


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
