"""认证 API 模块。

实现用户认证相关的 RESTful API 端点。
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from motor.motor_asyncio import AsyncIOMotorCollection
from passlib.hash import bcrypt

from ...models.user import UserDocument
from ...repository.user_repo import UserRepository
from ..auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
)
from ..dependencies import get_current_user, get_role_collection, get_user_repo

router = APIRouter(prefix="/auth", tags=["认证"])

AUTH_API_DESCRIPTION = """
认证 API 提供用户登录认证和令牌管理功能。

## 认证方式

系统使用 JWT (JSON Web Token) 进行身份认证：

- **Access Token**：有效期 15 分钟，用于 API 请求认证
- **Refresh Token**：有效期 7 天，用于刷新 Access Token

## 使用方式

在请求头中添加：
```
Authorization: Bearer <access_token>
```
"""


@router.post(
    "/token",
    summary="用户登录",
    description="""
使用用户名和密码获取访问令牌。

## 请求格式

使用 `application/x-www-form-urlencoded` 格式提交：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

## 响应示例

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 错误码

| 状态码 | 说明 |
|--------|------|
| 401 | 用户名或密码错误 |
""",
    responses={
        200: {
            "description": "登录成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {"description": "用户名或密码错误"},
    },
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: UserRepository = Depends(get_user_repo),
    role_collection: AsyncIOMotorCollection = Depends(get_role_collection),
):
    """获取 Access Token。"""
    user = await user_repo.find_by_username(form_data.username)
    if user is None or not bcrypt.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从数据库加载用户角色
    user_roles = await user_repo.get_user_roles(user.id, role_collection)
    role_names = [role.get("name", "") for role in user_roles]

    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        user_id=user.id,
        roles=role_names,
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh",
    summary="刷新令牌",
    description="""
使用 Refresh Token 获取新的 Access Token。

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | 是 | 刷新令牌 |

## 响应示例

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 错误码

| 状态码 | 说明 |
|--------|------|
| 401 | Refresh Token 无效或已过期 |
""",
    responses={
        200: {
            "description": "刷新成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {"description": "Refresh Token 无效"},
    },
)
async def refresh_token(
    refresh_token: str,
    user_repo: UserRepository = Depends(get_user_repo),
    role_collection: AsyncIOMotorCollection = Depends(get_role_collection),
):
    """刷新 Access Token。"""
    try:
        payload = verify_access_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的 Refresh Token",
            )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的 Refresh Token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Refresh Token",
        )

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    # 从数据库加载用户角色
    user_roles = await user_repo.get_user_roles(user.id, role_collection)
    role_names = [role.get("name", "") for role in user_roles]

    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        user_id=user.id,
        roles=role_names,
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    summary="获取当前用户信息",
    description="""
获取当前已认证用户的详细信息。

## 响应示例

```json
{
  "id": "user_abc123",
  "username": "admin",
  "email": "admin@example.com",
  "display_name": "管理员",
  "roles": ["admin", "editor"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 错误码

| 状态码 | 说明 |
|--------|------|
| 401 | 未授权 - 需要有效的 Access Token |
""",
    responses={
        200: {
            "description": "成功获取用户信息",
            "content": {
                "application/json": {
                    "example": {
                        "id": "user_abc123",
                        "username": "admin",
                        "email": "admin@example.com",
                        "display_name": "管理员",
                        "roles": ["admin", "editor"],
                    }
                }
            },
        },
        401: {"description": "未授权"},
    },
)
async def get_current_user_info(
    current_user: UserDocument = Depends(get_current_user),
):
    """获取当前用户信息。"""
    return current_user.to_response()
