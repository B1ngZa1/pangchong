"""
胖虫电商系统 - 认证 API
"""
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional

from ..core.database import get_db
from ..core.config import settings
from ..core.security import (
    verify_password,
    get_password_hash,
    create_tokens,
    verify_token,
    get_current_user,
)
from ..models.user import User, UserAddress
from ..schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
    UserResponse,
    UserUpdate,
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)

router = APIRouter(prefix="/auth", tags=["认证"])


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Keep the long-lived credential out of JavaScript-readable storage."""
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path="/api/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path="/api/auth",
    )


def _token_response(tokens: dict[str, str], request: Request) -> dict[str, Optional[str]]:
    """Return cookie-first auth data; require an explicit legacy opt-in."""
    if request.headers.get("x-token-transport", "").casefold() == "body":
        return tokens
    return {
        "access_token": tokens["access_token"],
        "refresh_token": None,
        "token_type": tokens["token_type"],
    }


# ============ 注册 ============

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    用户注册

    - **username**: 用户名（3-50字符，唯一）
    - **email**: 邮箱（唯一）
    - **password**: 密码（6-100字符）
    - **phone**: 手机号（可选）
    """
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 检查手机号是否已存在
    if user_data.phone:
        result = await db.execute(select(User).where(User.phone == user_data.phone))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )

    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        nickname=user_data.nickname or user_data.username,
        password_hash=get_password_hash(user_data.password),
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名、邮箱或手机号已存在（并发冲突）"
        )

    # 生成 Token
    tokens = create_tokens(str(user.id))
    _set_refresh_cookie(response, tokens["refresh_token"])
    return _token_response(tokens, request)


# ============ 登录 ============

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录

    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    # 查找用户（支持用户名或邮箱登录）
    result = await db.execute(
        select(User).where(
            or_(
                User.username == login_data.username,
                User.email == login_data.username
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 生成 Token
    tokens = create_tokens(str(user.id))
    _set_refresh_cookie(response, tokens["refresh_token"])
    return _token_response(tokens, request)


# ============ 刷新 Token ============

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    token_data: Optional[TokenRefresh] = Body(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    刷新访问 Token

    - **refresh_token**: 刷新 Token
    """
    # Cookie auth is the production path.  The body remains accepted as a
    # short-lived compatibility bridge for existing non-browser clients.
    supplied_token = token_data.refresh_token if token_data else None
    refresh_value = supplied_token or request.cookies.get(settings.AUTH_REFRESH_COOKIE_NAME)
    payload = verify_token(refresh_value or "", token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新 Token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token"
        )

    # 验证用户是否存在
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )

    # 生成新的 Token
    tokens = create_tokens(user_id)
    _set_refresh_cookie(response, tokens["refresh_token"])
    return _token_response(tokens, request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> Response:
    """Revoke the browser refresh session cookie."""
    _clear_refresh_cookie(response)
    return response


# ============ 获取当前用户信息 ============

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user


# ============ 更新用户信息 ============

@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息

    - **nickname**: 昵称
    - **phone**: 手机号
    - **avatar_url**: 头像URL
    """
    # 检查手机号是否已被使用
    if user_data.phone and user_data.phone != current_user.phone:
        result = await db.execute(select(User).where(User.phone == user_data.phone))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被使用"
            )

    # 更新字段
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    await db.flush()
    return current_user


# ============ 修改密码 ============

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码

    - **old_password**: 旧密码
    - **new_password**: 新密码（6-100字符）
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.flush()

    return {"message": "密码修改成功"}


# ============ 地址管理 ============

@router.get("/addresses", response_model=list[AddressResponse])
async def get_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的所有地址"""
    result = await db.execute(
        select(UserAddress)
        .where(UserAddress.user_id == current_user.id)
        .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
    )
    return result.scalars().all()


@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建新地址"""
    # 如果设置为默认地址，先取消其他默认地址
    if address_data.is_default:
        result = await db.execute(
            select(UserAddress).where(
                UserAddress.user_id == current_user.id,
                UserAddress.is_default == True
            )
        )
        for addr in result.scalars().all():
            addr.is_default = False

    address = UserAddress(
        user_id=current_user.id,
        **address_data.dict()
    )
    db.add(address)
    await db.flush()
    return address


@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    address_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新地址"""
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id
        )
    )
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地址不存在"
        )

    # 如果设置为默认地址，先取消其他默认地址
    if address_data.is_default and not address.is_default:
        result = await db.execute(
            select(UserAddress).where(
                UserAddress.user_id == current_user.id,
                UserAddress.is_default == True
            )
        )
        for addr in result.scalars().all():
            addr.is_default = False

    # 更新字段
    for field, value in address_data.dict(exclude_unset=True).items():
        setattr(address, field, value)

    await db.flush()
    return address


@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除地址"""
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id
        )
    )
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地址不存在"
        )

    await db.delete(address)
    return {"message": "地址已删除"}
