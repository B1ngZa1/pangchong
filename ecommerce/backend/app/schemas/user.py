"""
胖虫电商系统 - 用户相关 Schema
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


# ============ 用户认证 ============

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, max_length=100, description="密码（8-100字符，需包含大写字母和数字）")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含至少一个数字")
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


class PasswordChange(BaseModel):
    """修改密码"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码（8-100字符，需包含大写字母和数字）")

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含至少一个数字")
        return v


# ============ 用户信息 ============

class UserBase(BaseModel):
    """用户基本信息"""
    username: str
    email: str
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """用户信息响应"""
    id: UUID
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """更新用户信息"""
    nickname: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")
    avatar_url: Optional[str] = None


# ============ 用户地址 ============

class AddressCreate(BaseModel):
    """创建地址请求"""
    recipient_name: str = Field(..., max_length=50, description="收件人姓名")
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    province: str = Field(..., max_length=50, description="省份")
    city: str = Field(..., max_length=50, description="城市")
    district: str = Field(..., max_length=50, description="区县")
    address: str = Field(..., max_length=200, description="详细地址")
    postal_code: Optional[str] = Field(None, max_length=10, description="邮编")
    is_default: bool = Field(False, description="是否默认地址")


class AddressUpdate(BaseModel):
    """更新地址请求（所有字段可选）"""
    recipient_name: Optional[str] = Field(None, max_length=50, description="收件人姓名")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    district: Optional[str] = Field(None, max_length=50, description="区县")
    address: Optional[str] = Field(None, max_length=200, description="详细地址")
    postal_code: Optional[str] = Field(None, max_length=10, description="邮编")
    is_default: Optional[bool] = Field(None, description="是否默认地址")


class AddressResponse(BaseModel):
    """地址响应"""
    id: UUID
    recipient_name: str
    phone: str
    province: str
    city: str
    district: str
    address: str
    postal_code: Optional[str]
    is_default: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
