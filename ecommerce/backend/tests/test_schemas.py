"""
Tests for Pydantic validation schemas.
"""
import pytest
from pydantic import ValidationError
from app.schemas.user import UserRegister, PasswordChange, AddressCreate
from app.schemas.order import CustomOrderItemCreate


class TestUserRegister:
    def test_valid_registration(self):
        data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass1",
            phone="13800138001",
        )
        assert data.username == "testuser"
        assert data.email == "test@example.com"

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="Ab1",
            )

    def test_password_no_uppercase(self):
        with pytest.raises(ValidationError) as e:
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="testpass1",
            )
        assert "大写" in str(e.value)

    def test_password_no_digit(self):
        with pytest.raises(ValidationError) as e:
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="TestPassword",
            )
        assert "数字" in str(e.value)

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserRegister(
                username="testuser",
                email="not-an-email",
                password="SecurePass1",
            )

    def test_username_too_short(self):
        with pytest.raises(ValidationError):
            UserRegister(
                username="ab",
                email="test@example.com",
                password="SecurePass1",
            )

    def test_invalid_phone_format(self):
        with pytest.raises(ValidationError):
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="SecurePass1",
                phone="12345678901",
            )

    def test_optional_phone(self):
        data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="SecurePass1",
        )
        assert data.phone is None


class TestPasswordChange:
    def test_new_password_must_be_strong(self):
        with pytest.raises(ValidationError):
            PasswordChange(old_password="old", new_password="weak")

    def test_valid_change(self):
        data = PasswordChange(old_password="oldpass", new_password="NewPass1")
        assert data.old_password == "oldpass"
        assert data.new_password == "NewPass1"


class TestAddress:
    def test_valid_address(self):
        data = AddressCreate(
            recipient_name="张三",
            phone="13800138001",
            province="广东省",
            city="深圳市",
            district="南山区",
            address="科技园路1号",
        )
        assert data.recipient_name == "张三"

    def test_invalid_phone(self):
        with pytest.raises(ValidationError):
            AddressCreate(
                recipient_name="张三",
                phone="12345",
                province="广东省",
                city="深圳市",
                district="南山区",
                address="科技园路1号",
            )


class TestCustomOrderItem:
    def test_valid_custom_item(self):
        data = CustomOrderItemCreate(
            configuration={
                "configuration_id": "diy-pc",
                "version": 1,
                "variant_id": "black",
                "material_id": "matte",
                "parts": [{
                    "slot_id": "cpu",
                    "product_id": "11111111-1111-1111-1111-111111111111",
                    "quantity": 1,
                }],
            },
            quantity=1,
        )
        assert data.configuration.configuration_id == "diy-pc"
        assert data.configuration.parts[0].slot_id == "cpu"

    def test_rejects_client_price(self):
        with pytest.raises(ValidationError):
            CustomOrderItemCreate(
                configuration={
                    "configuration_id": "diy-pc",
                    "version": 1,
                    "variant_id": "black",
                    "material_id": "matte",
                    "parts": [{
                        "slot_id": "cpu",
                        "product_id": "11111111-1111-1111-1111-111111111111",
                    }],
                },
                quantity=1,
                price="0.01",
            )


class TestProductAssetMetadata:
    def test_accepts_model_transform_and_price_source(self):
        from app.schemas.product import ProductCreate

        product = ProductCreate(
            name="Demo Case",
            slug="demo-case",
            price=999,
            model_3d_url="https://example.com/demo.glb",
            model_3d_scale=1.25,
            model_3d_position=[0, 1, 0],
            model_3d_rotation=[0, 0, 0],
            asset_license="CC BY 4.0",
            asset_source_url="https://example.com/model-source",
            price_source_name="Vendor",
            price_source_url="https://example.com/product",
        )
        assert product.model_3d_position == [0.0, 1.0, 0.0]
        assert product.asset_source_url == "https://example.com/model-source"

    def test_model_requires_license_and_source_before_catalog_binding(self):
        from fastapi import HTTPException

        from app.api.products import _validate_asset_provenance

        with pytest.raises(HTTPException) as exc_info:
            _validate_asset_provenance("https://example.com/demo.glb", "", "")
        assert exc_info.value.status_code == 422
        assert "素材许可" in exc_info.value.detail
        assert "素材来源 URL" in exc_info.value.detail

    def test_rejects_incomplete_model_transform(self):
        from app.schemas.product import ProductCreate

        with pytest.raises(ValidationError):
            ProductCreate(
                name="Demo Case",
                slug="demo-case",
                price=999,
                model_3d_position=[0, 1],
            )

    def test_product_brief_exposes_price_provenance(self):
        from datetime import datetime, timezone
        from uuid import uuid4

        from app.schemas.product import ProductBrief

        checked_at = datetime(2026, 6, 30, tzinfo=timezone.utc)
        product = ProductBrief(
            id=uuid4(),
            name="Demo Case",
            slug="demo-case",
            price=999,
            original_price=None,
            image_url=None,
            brand="Pangchong",
            sold_count=0,
            is_in_stock=True,
            price_source_name="Brand site",
            price_source_url="https://example.com/product",
            price_checked_at=checked_at,
        )

        assert product.price_source_name == "Brand site"
        assert product.price_source_url == "https://example.com/product"
        assert product.price_checked_at == checked_at
