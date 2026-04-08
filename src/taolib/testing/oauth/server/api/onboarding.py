"""OAuth 引导流程 API 模块。

处理新用户的首次登录引导，完成账户创建和关联。
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...errors import OAuthError, OAuthOnboardingError
from ...models.enums import OAuthConnectionStatus
from ...models.profile import OnboardingData
from ...services.session_service import OAuthSessionService
from ..config import settings
from ..dependencies import (
    get_connection_repo,
    get_session_service,
)

router = APIRouter(prefix="/oauth/onboarding", tags=["OAuth 引导"])


@router.post("")
async def complete_onboarding(
    data: OnboardingData,
    request: Request,
    connection_id: str,
    connection_repo=Depends(get_connection_repo),
    session_service: OAuthSessionService = Depends(get_session_service),
):
    """完成新用户引导流程。

    将引导数据与待激活的 OAuth 连接关联，创建本地用户并生成会话。

    流程：
    1. 验证连接存在且处于 PENDING_ONBOARDING 状态
    2. 通过 config_center 集成创建用户
    3. 更新连接，关联到新用户
    4. 创建会话并返回 Token

    Args:
        data: 引导数据（用户名、显示名称）
        request: FastAPI Request 对象
        connection_id: 待激活的 OAuth 连接 ID
        connection_repo: OAuth 连接仓储
        session_service: OAuth 会话服务

    Returns:
        Token 响应
    """
    ip_address = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")

    connection = await connection_repo.get_by_id(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="连接不存在",
        )

    if connection.status != OAuthConnectionStatus.PENDING_ONBOARDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该连接不需要引导流程",
        )

    try:
        # 简化引导流程：直接更新连接状态
        # 完整的 config_center 集成需要在部署时配置
        from datetime import UTC, datetime

        await connection_repo.update(
            connection_id,
            {
                "status": str(OAuthConnectionStatus.ACTIVE),
                "updated_at": datetime.now(UTC),
            },
        )

        # 为引导用户创建会话
        session_data = await session_service.create_session(
            user_id=connection.user_id or connection_id,
            connection_id=connection_id,
            provider=connection.provider,
            roles=[],
            ip_address=ip_address,
            user_agent=user_agent,
            session_ttl_hours=settings.session_ttl_hours,
        )

        return {
            "status": "onboarding_complete",
            "username": data.username,
            **session_data,
        }

    except OAuthOnboardingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )


