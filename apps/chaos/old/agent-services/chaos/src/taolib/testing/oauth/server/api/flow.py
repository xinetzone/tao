"""OAuth 授权流程 API 模块。

实现 OAuth2 授权码流程的端点：生成授权 URL 和处理回调。
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from ...errors import (
    OAuthCredentialNotFoundError,
    OAuthError,
    OAuthStateError,
)
from ...models.enums import OAuthConnectionStatus
from ...services.account_service import OAuthAccountService
from ...services.flow_service import OAuthFlowService
from ...services.session_service import OAuthSessionService
from ..config import settings
from ..dependencies import (
    get_account_service,
    get_flow_service,
    get_session_service,
)

router = APIRouter(prefix="/oauth", tags=["OAuth 流程"])

OAUTH_FLOW_DESCRIPTION = """
OAuth 授权流程 API 实现标准的 OAuth2 授权码流程。

## 支持的提供商

- **GitHub**：使用 GitHub 账号登录
- **Google**：使用 Google 账号登录

## 授权流程

1. 前端调用 `/oauth/authorize-url/{provider}` 获取授权 URL
2. 重定向用户到 OAuth 提供商授权页面
3. 用户授权后被重定向回 `/oauth/callback/{provider}`
4. 系统交换授权码获取用户信息并创建会话
5. 返回 JWT Token 给客户端

## 账户关联

已登录用户可以通过 `/oauth/connections/link/{provider}` 将新的 OAuth 提供商关联到现有账户。
"""


@router.get(
    "/authorize/{provider}",
    summary="发起 OAuth 授权",
    description="""
生成 OAuth 授权 URL 并重定向用户到提供商授权页面。

## 路径参数

- `provider`: OAuth 提供商名称（github/google）

## 查询参数

- `link`: 设为 `true` 可将新提供商关联到已登录账户

## 响应

重定向到 OAuth 提供商授权页面（HTTP 302）

## 示例

```
GET /oauth/authorize/github
GET /oauth/authorize/google?link=true&user_id=user_123
```
""",
    responses={
        302: {"description": "重定向到 OAuth 提供商授权页面"},
        400: {"description": "OAuth 错误"},
        404: {"description": "提供商未配置"},
    },
)
async def authorize(
    provider: str,
    request: Request,
    flow_service: OAuthFlowService = Depends(get_flow_service),
    user_id: str | None = None,
):
    """生成 OAuth 授权 URL 并重定向。"""
    link = request.query_params.get("link", "").lower() == "true"
    extra_state: dict[str, Any] | None = None
    if link and user_id:
        extra_state = {"link_to_user_id": user_id}

    try:
        authorize_url, _ = await flow_service.generate_authorize_url(
            provider=provider,
            extra_state=extra_state,
        )
        return RedirectResponse(url=authorize_url, status_code=302)
    except OAuthCredentialNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get(
    "/authorize-url/{provider}",
    summary="获取授权 URL",
    description="""
获取 OAuth 授权 URL（不自动重定向）。

适用于前端 SPA 应用需要自行处理重定向的场景。

## 路径参数

- `provider`: OAuth 提供商名称（github/google）

## 查询参数

- `redirect_uri`: 自定义回调 URI（可选）

## 响应示例

```json
{
  "authorize_url": "https://github.com/login/oauth/authorize?client_id=xxx&state=yyy",
  "state": "csrf_state_token"
}
```

## 安全说明

返回的 `state` 参数用于 CSRF 防护，回调时必须验证。
""",
    responses={
        200: {
            "description": "成功获取授权 URL",
            "content": {
                "application/json": {
                    "example": {
                        "authorize_url": "https://github.com/login/oauth/authorize?client_id=xxx",
                        "state": "csrf_state_token",
                    }
                }
            },
        },
        400: {"description": "OAuth 错误"},
        404: {"description": "提供商未配置"},
    },
)
async def get_authorize_url(
    provider: str,
    flow_service: OAuthFlowService = Depends(get_flow_service),
    redirect_uri: str | None = Query(default=None, description="自定义回调 URI"),
):
    """获取 OAuth 授权 URL（不自动重定向）。"""
    try:
        authorize_url, state = await flow_service.generate_authorize_url(
            provider=provider,
            redirect_uri=redirect_uri,
        )
        return {"authorize_url": authorize_url, "state": state}
    except OAuthCredentialNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get(
    "/callback/{provider}",
    summary="OAuth 回调处理",
    description="""
处理 OAuth 提供商的授权回调。

## 流程说明

1. 验证 state 参数（CSRF 防护）
2. 使用授权码交换访问令牌
3. 获取用户信息
4. 查找或创建 OAuth 连接
5. 创建会话并返回 Token

## 路径参数

- `provider`: OAuth 提供商名称

## 查询参数

- `code`: OAuth 授权码（必填）
- `state`: CSRF state token（必填）

## 响应示例

**新用户（需要引导）：**
```json
{
  "status": "onboarding_required",
  "connection_id": "conn_abc123",
  "provider": "github",
  "email": "user@example.com",
  "display_name": "John Doe",
  "avatar_url": "https://avatar.url"
}
```

**已注册用户：**
```json
{
  "status": "authenticated",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```
""",
    responses={
        200: {"description": "认证成功或需要引导"},
        400: {"description": "State 验证失败"},
        404: {"description": "提供商未配置"},
        502: {"description": "OAuth 提供商通信错误"},
    },
)
async def callback(
    provider: str,
    request: Request,
    code: str = Query(..., description="授权码"),
    state: str = Query(..., description="CSRF state token"),
    flow_service: OAuthFlowService = Depends(get_flow_service),
    account_service: OAuthAccountService = Depends(get_account_service),
    session_service: OAuthSessionService = Depends(get_session_service),
):
    """处理 OAuth 回调。"""
    ip_address = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")

    try:
        user_info, token_data = await flow_service.exchange_code(
            provider=provider,
            code=code,
            state=state,
        )

        connection, is_new_user = await account_service.find_or_create_connection(
            user_info=user_info,
            token_data=token_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if is_new_user or connection.status == OAuthConnectionStatus.PENDING_ONBOARDING:
            return {
                "status": "onboarding_required",
                "connection_id": connection.id,
                "provider": provider,
                "email": user_info.email,
                "display_name": user_info.display_name,
                "avatar_url": user_info.avatar_url,
            }

        session_data = await session_service.create_session(
            user_id=connection.user_id,
            connection_id=connection.id,
            provider=provider,
            roles=[],
            ip_address=ip_address,
            user_agent=user_agent,
            session_ttl_hours=settings.session_ttl_hours,
        )

        return {
            "status": "authenticated",
            **session_data,
        }

    except OAuthStateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except OAuthCredentialNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.message,
        )
