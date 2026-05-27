"""OAuth 账户连接 API 模块。

管理用户的 OAuth 提供商连接（查看、关联、解除关联）。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from ...errors import OAuthAlreadyLinkedError, OAuthCannotUnlinkError, OAuthError
from ...models.connection import OAuthConnectionResponse
from ...services.account_service import OAuthAccountService
from ...services.flow_service import OAuthFlowService
from ..dependencies import (
    get_account_service,
    get_current_user_id,
    get_flow_service,
)

router = APIRouter(prefix="/oauth/connections", tags=["OAuth 连接"])


@router.get("", response_model=list[OAuthConnectionResponse])
async def list_connections(
    user_id: str = Depends(get_current_user_id),
    account_service: OAuthAccountService = Depends(get_account_service),
):
    """获取当前用户的所有 OAuth 连接。

    Args:
        user_id: 当前用户 ID
        account_service: OAuth 账户服务

    Returns:
        OAuth 连接列表
    """
    return await account_service.get_user_connections(user_id)


@router.post("/link/{provider}")
async def link_provider(
    provider: str,
    request: Request,
    flow_service: OAuthFlowService = Depends(get_flow_service),
    user_id: str = Depends(get_current_user_id),
):
    """发起将新提供商关联到当前用户的流程。

    生成带有 link_to_user_id 的授权 URL。

    Args:
        provider: OAuth 提供商名称
        request: FastAPI Request 对象
        flow_service: OAuth 流程服务
        user_id: 当前用户 ID

    Returns:
        包含授权 URL 的响应
    """
    try:
        authorize_url, state = await flow_service.generate_authorize_url(
            provider=provider,
            extra_state={"link_to_user_id": user_id},
        )
        return {"authorize_url": authorize_url, "state": state}
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post("/link/{provider}/complete")
async def complete_link(
    provider: str,
    request: Request,
    code: str = Query(..., description="授权码"),
    state: str = Query(..., description="CSRF state token"),
    flow_service: OAuthFlowService = Depends(get_flow_service),
    account_service: OAuthAccountService = Depends(get_account_service),
    user_id: str = Depends(get_current_user_id),
):
    """完成提供商关联流程。

    使用授权码交换用户信息并关联到当前账户。

    Args:
        provider: OAuth 提供商名称
        request: FastAPI Request 对象
        code: 授权码
        state: CSRF state token
        flow_service: OAuth 流程服务
        account_service: OAuth 账户服务
        user_id: 当前用户 ID

    Returns:
        关联成功的连接信息
    """
    ip_address = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")

    try:
        user_info, token_data = await flow_service.exchange_code(
            provider=provider,
            code=code,
            state=state,
        )

        connection = await account_service.link_provider(
            user_id=user_id,
            user_info=user_info,
            token_data=token_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return {"status": "linked", "connection": connection.to_response()}

    except OAuthAlreadyLinkedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.delete("/{provider}")
async def unlink_provider(
    provider: str,
    request: Request,
    account_service: OAuthAccountService = Depends(get_account_service),
    user_id: str = Depends(get_current_user_id),
    has_password: bool = Query(default=False, description="用户是否设置了密码"),
):
    """解除当前用户与提供商的关联。

    确保至少保留一种认证方式。

    Args:
        provider: OAuth 提供商名称
        request: FastAPI Request 对象
        account_service: OAuth 账户服务
        user_id: 当前用户 ID
        has_password: 用户是否有密码（用于安全校验）

    Returns:
        解除关联的结果
    """
    ip_address = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")

    try:
        result = await account_service.unlink_provider(
            user_id=user_id,
            provider=provider,
            has_password=has_password,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到指定提供商的连接",
            )

        return {"status": "unlinked", "provider": provider}

    except OAuthCannotUnlinkError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
