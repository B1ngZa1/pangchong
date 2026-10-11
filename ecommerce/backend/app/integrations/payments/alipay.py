"""Alipay RSA2 payment adapter.

This module contains provider-specific signing and notification parsing only.
Order state transitions and database idempotency live in the payment service.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Callable, Mapping, Optional
from urllib.parse import urlencode
from uuid import UUID

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from ...core.config import settings


class AlipayCallbackError(ValueError):
    """A provider callback failed verification or required-field validation."""


@dataclass(frozen=True)
class AlipayCallback:
    """Verified, normalized fields needed by the payment service."""

    order_no: str
    trade_no: str
    trade_status: str
    amount: Decimal
    app_id: str
    notification_id: Optional[str]
    event_key: str
    dedupe_key: str
    payload_hash: str
    received_at: datetime


def _as_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def _normalize_pem(value: str) -> str:
    # Environment variables commonly carry PEM newlines as the two characters
    # "\\n".  This changes formatting only; it never logs or exposes the key.
    return value.replace("\\n", "\n").strip()


def _money(value: object) -> Decimal:
    try:
        amount = Decimal(_as_text(value).strip())
    except (InvalidOperation, AttributeError, TypeError, ValueError) as exc:
        raise AlipayCallbackError("金额格式无效") from exc
    if not amount.is_finite() or amount < 0:
        raise AlipayCallbackError("金额格式无效")
    return amount


class AlipayPaymentAdapter:
    """Small, dependency-injected Alipay adapter suitable for sandbox tests."""

    _ALLOWED_STATUSES = frozenset({
        "WAIT_BUYER_PAY",
        "TRADE_SUCCESS",
        "TRADE_FINISHED",
        "TRADE_CLOSED",
    })

    def __init__(
        self,
        *,
        app_id: Optional[str] = None,
        private_key: Optional[str] = None,
        public_key: Optional[str] = None,
        gateway: Optional[str] = None,
        sandbox: Optional[bool] = None,
        notify_url: Optional[str] = None,
        return_url: Optional[str] = None,
        seller_id: Optional[str] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.app_id = settings.ALIPAY_APP_ID if app_id is None else app_id
        self.private_key = settings.ALIPAY_PRIVATE_KEY if private_key is None else private_key
        self.public_key = settings.ALIPAY_PUBLIC_KEY if public_key is None else public_key
        self.gateway = settings.ALIPAY_GATEWAY if gateway is None else gateway
        self.sandbox = settings.ALIPAY_SANDBOX if sandbox is None else sandbox
        self.notify_url = getattr(settings, "ALIPAY_NOTIFY_URL", "") if notify_url is None else notify_url
        self.return_url = getattr(settings, "ALIPAY_RETURN_URL", "") if return_url is None else return_url
        self.seller_id = getattr(settings, "ALIPAY_SELLER_ID", "") if seller_id is None else seller_id
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def build_sign_content(params: Mapping[str, object]) -> str:
        """Build Alipay's canonical RSA2 content without mutating input."""
        pairs: list[str] = []
        for key in sorted(params):
            if key in {"sign", "sign_type"}:
                continue
            value = params[key]
            if value is None or value == "":
                continue
            pairs.append(f"{key}={_as_text(value)}")
        return "&".join(pairs)

    def _private_key_object(self):
        if not self.private_key.strip():
            raise AlipayCallbackError("支付宝支付未配置私钥")
        try:
            return serialization.load_pem_private_key(
                _normalize_pem(self.private_key).encode("utf-8"),
                password=None,
            )
        except (TypeError, ValueError, IndexError) as exc:
            raise AlipayCallbackError("支付宝私钥配置无效") from exc

    def _public_key_object(self):
        if not self.public_key.strip():
            raise AlipayCallbackError("支付宝回调验签未配置公钥")
        try:
            return serialization.load_pem_public_key(_normalize_pem(self.public_key).encode("utf-8"))
        except (TypeError, ValueError, IndexError) as exc:
            raise AlipayCallbackError("支付宝公钥配置无效") from exc

    def sign_params(self, params: Mapping[str, object]) -> str:
        """Sign canonical parameters with RSA2 (SHA-256 + PKCS#1 v1.5)."""
        content = self.build_sign_content(params)
        signature = self._private_key_object().sign(
            content.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("ascii")

    def verify_callback(self, params: Mapping[str, object]) -> bool:
        """Require the configured app and a valid RSA2 signature in every mode."""
        if not self.app_id or _as_text(params.get("app_id", "")) != self.app_id:
            return False
        if self.seller_id and _as_text(params.get("seller_id", "")) != self.seller_id:
            return False
        if _as_text(params.get("sign_type", "")) != "RSA2":
            return False

        signature_text = _as_text(params.get("sign", ""))
        if not signature_text:
            return False
        try:
            signature = base64.b64decode(signature_text, validate=True)
            self._public_key_object().verify(
                signature,
                self.build_sign_content(params).encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        except (AlipayCallbackError, InvalidSignature, ValueError, TypeError):
            return False
        return True

    def parse_callback(self, params: Mapping[str, object]) -> AlipayCallback:
        """Verify and normalize a callback before it reaches order state."""
        if not self.verify_callback(params):
            raise AlipayCallbackError("支付宝回调验签失败")

        required = {
            "out_trade_no": "订单号",
            "trade_no": "交易流水号",
            "trade_status": "交易状态",
            "total_amount": "金额",
        }
        values: dict[str, str] = {}
        for field, label in required.items():
            value = _as_text(params.get(field, "")).strip()
            if not value:
                raise AlipayCallbackError(f"缺少{label}")
            values[field] = value

        status = values["trade_status"]
        if status not in self._ALLOWED_STATUSES:
            raise AlipayCallbackError("交易状态不受支持")

        amount = _money(values["total_amount"])
        payload_hash = hashlib.sha256(self.build_sign_content(params).encode("utf-8")).hexdigest()
        notification_id = _as_text(params.get("notify_id", "")).strip() or None
        event_key = notification_id or payload_hash
        normalized_amount = amount.quantize(Decimal("0.01"))
        dedupe_material = "|".join(
            ("alipay", values["out_trade_no"], values["trade_no"], status, format(normalized_amount, "f"))
        )
        dedupe_key = hashlib.sha256(dedupe_material.encode("utf-8")).hexdigest()

        return AlipayCallback(
            order_no=values["out_trade_no"],
            trade_no=values["trade_no"],
            trade_status=status,
            amount=amount,
            app_id=self.app_id,
            notification_id=notification_id,
            event_key=event_key,
            dedupe_key=dedupe_key,
            payload_hash=payload_hash,
            received_at=self._clock(),
        )

    def create_payment_url(
        self,
        order_no: str,
        amount: Decimal | str | float,
        subject: str,
        order_id: Optional[UUID] = None,
    ) -> str:
        """Create a signed page-pay URL, or the local sandbox handoff."""
        if self.sandbox:
            if order_id is None:
                raise ValueError("沙箱支付缺少订单 ID")
            return f"/sandbox/orders/{order_id}"

        if not self.app_id or not self.private_key.strip():
            raise ValueError("支付宝支付未配置完整凭证")

        payment_amount = _money(amount).quantize(Decimal("0.01"))
        params: dict[str, str] = {
            "app_id": self.app_id,
            "method": "alipay.trade.page.pay",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": self._clock().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": json.dumps(
                {
                    "out_trade_no": order_no,
                    "product_code": "FAST_INSTANT_TRADE_PAY",
                    "total_amount": format(payment_amount, "f"),
                    "subject": subject,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        }
        if self.notify_url:
            params["notify_url"] = self.notify_url
        if self.return_url:
            params["return_url"] = self.return_url
        params["sign"] = self.sign_params(params)
        return f"{self.gateway}?{urlencode(params)}"
