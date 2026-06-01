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
            product_name="Custom PC Build",
            price=12999,
            quantity=1,
            product_specs={"CPU": "Ryzen 9", "GPU": "RTX 5090"},
        )
        assert data.product_name == "Custom PC Build"
        assert data.product_specs["CPU"] == "Ryzen 9"

    def test_rejects_zero_price(self):
        with pytest.raises(ValidationError):
            CustomOrderItemCreate(product_name="Custom PC Build", price=0, quantity=1)
