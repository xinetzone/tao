"""OAuth 会话管理 API 模块。

管理用户的 OAuth 会话（查看、刷新、撤销）。
"""

from fastapi import APIRouter, Depends, HTTPException, status

from ...models.session import OAuthSessionResponse
from ...services.session_service import OAuthSessionService
from ..dependencies import get_current_user_id, get_session_service

router = APIRouter(prefix="/oauth/sessions", tags=["OAuth 会话"])


@router.get("", response_model=list[OAuthSessionResponse])
async def list_sessions(
    user_id: str = Depends(get_current_user_id),
    session_service: OAuthSessionService = Depends(get_session_service),
):
    """列出当前用户的所有活跃会话。

    Args:
        user_id: 当前用户 ID
        session_service: OAuth 会话服务

    Returns:
        活跃会话列表
    """
    return await session_service.list_active_sessions(user_id)


@router.post("/{session_id}/refresh")
async def refresh_session(
    session_id: str,
    session_service: OAuthSessionService = Depends(get_session_service),
    user_id: str = Depends(get_current_user_id),
):
    """刷新指定会话的 JWT Token。

    Args:
        session_id: 会话 ID
        session_service: OAuth 会话服务
        user_id: 当前用户 ID

    Returns:
        新的 Token 响应
    """
    result = await session_service.refresh_session(session_id, roles=[])
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或已过期",
        )
    return result


@router.delete("/{session_id}")
async def revoke_session(
    session_id: str,
    session_service: OAuthSessionService = Depends(get_session_service),
    user_id: str = Depends(get_current_user_id),
):
    """撤销指定会话。

    Args:
        session_id: 会话 ID
        session_service: OAuth 会话服务
        user_id: 当前用户 ID

    Returns:
        撤销结果
    """
    result = await session_service.revoke_session(session_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )
    return {"status": "revoked", "session_id": session_id}


@router.delete("")
async def revoke_all_sessions(
    user_id: str = Depends(get_current_user_id),
    session_service: OAuthSessionService = Depends(get_session_service),
):
    """撤销当前用户的所有会话。

    Args:
        user_id: 当前用户 ID
        session_service: OAuth 会话服务

    Returns:
        撤销的会话数量
    """
    count = await session_service.revoke_all_sessions(user_id)
    return {"status": "all_revoked", "revoked_count": count}


