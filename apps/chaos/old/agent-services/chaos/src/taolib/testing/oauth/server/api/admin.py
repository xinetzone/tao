"""OAuth 管理 API 模块。

提供 OAuth 应用凭证管理和活动监控的管理端点。
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...models.activity import OAuthActivityLogResponse
from ...models.credential import (
    OAuthAppCredentialCreate,
    OAuthAppCredentialResponse,
    OAuthAppCredentialUpdate,
)
from ...services.admin_service import OAuthAdminService
from ..dependencies import get_admin_service, get_current_user_id

router = APIRouter(prefix="/oauth/admin", tags=["OAuth 管理"])


@router.get("/credentials", response_model=list[OAuthAppCredentialResponse])
async def list_credentials(
    admin_service: OAuthAdminService = Depends(get_admin_service),
    user_id: str = Depends(get_current_user_id),
):
    """列出所有 OAuth 应用凭证。

    Args:
        admin_service: OAuth 管理服务
        user_id: 当前管理员用户 ID

    Returns:
        凭证列表（不含 client_secret）
    """
    return await admin_service.list_credentials()


@router.post(
    "/credentials",
    response_model=OAuthAppCredentialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_credential(
    data: OAuthAppCredentialCreate,
    admin_service: OAuthAdminService = Depends(get_admin_service),
    user_id: str = Depends(get_current_user_id),
):
    """创建 OAuth 应用凭证。

    Args:
        data: 凭证创建数据
        admin_service: OAuth 管理服务
        user_id: 当前管理员用户 ID

    Returns:
        创建的凭证响应
    """
    return await admin_service.create_credential(data, admin_user_id=user_id)


@router.put("/credentials/{credential_id}", response_model=OAuthAppCredentialResponse)
async def update_credential(
    credential_id: str,
    data: OAuthAppCredentialUpdate,
    admin_service: OAuthAdminService = Depends(get_admin_service),
    user_id: str = Depends(get_current_user_id),
):
    """更新 OAuth 应用凭证。

    Args:
        credential_id: 凭证 ID
        data: 凭证更新数据
        admin_service: OAuth 管理服务
        user_id: 当前管理员用户 ID

    Returns:
        更新后的凭证响应
    """
    result = await admin_service.update_credential(
        credential_id, data, admin_user_id=user_id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="凭证不存在",
        )
    return result


@router.delete("/credentials/{credential_id}")
async def delete_credential(
    credential_id: str,
    admin_service: OAuthAdminService = Depends(get_admin_service),
    user_id: str = Depends(get_current_user_id),
):
    """删除 OAuth 应用凭证。

    Args:
        credential_id: 凭证 ID
        admin_service: OAuth 管理服务
        user_id: 当前管理员用户 ID

    Returns:
        删除结果
    """
    result = await admin_service.delete_credential(credential_id, admin_user_id=user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="凭证不存在",
        )
    return {"status": "deleted", "credential_id": credential_id}


@router.get("/activity", response_model=list[OAuthActivityLogResponse])
async def get_activity_logs(
    admin_service: OAuthAdminService = Depends(get_admin_service),
    user_id_filter: str | None = Query(default=None, alias="user_id"),
    provider: str | None = Query(default=None),
    action: str | None = Query(default=None),
    log_status: str | None = Query(default=None, alias="status"),
    time_from: datetime | None = Query(default=None),
    time_to: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    _user_id: str = Depends(get_current_user_id),
):
    """查询 OAuth 活动日志。

    支持多维度过滤：用户、提供商、操作类型、状态、时间范围。

    Args:
        admin_service: OAuth 管理服务
        user_id_filter: 按用户 ID 过滤
        provider: 按提供商过滤
        action: 按操作类型过滤
        log_status: 按状态过滤
        time_from: 起始时间
        time_to: 结束时间
        skip: 跳过记录数
        limit: 限制记录数

    Returns:
        活动日志列表
    """
    return await admin_service.get_activity_logs(
        user_id=user_id_filter,
        provider=provider,
        action=action,
        status=log_status,
        time_from=time_from,
        time_to=time_to,
        skip=skip,
        limit=limit,
    )


@router.get("/stats")
async def get_stats(
    admin_service: OAuthAdminService = Depends(get_admin_service),
    _user_id: str = Depends(get_current_user_id),
):
    """获取 OAuth 连接和活动统计。

    返回总连接数、活跃连接数、各操作类型计数等统计数据。

    Args:
        admin_service: OAuth 管理服务

    Returns:
        统计数据字典
    """
    return await admin_service.get_stats()
