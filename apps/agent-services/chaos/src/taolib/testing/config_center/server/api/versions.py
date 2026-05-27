"""版本管理 API 模块。

实现版本历史和回滚的 RESTful API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, status

from ...cache.config_cache import ConfigCacheProtocol
from ...models.version import ConfigVersionResponse
from ...repository.audit_repo import AuditLogRepository
from ...repository.config_repo import ConfigRepository
from ...repository.version_repo import VersionRepository
from ...services.audit_service import AuditService
from ...services.config_service import ConfigService
from ...services.version_service import VersionService
from ..dependencies import (
    get_audit_repo,
    get_cache,
    get_config_repo,
    get_current_user,
    get_version_repo,
)

router = APIRouter(prefix="/configs/{config_id}/versions", tags=["版本管理"])


def _build_config_service(
    config_repo: ConfigRepository,
    version_repo: VersionRepository,
    audit_repo: AuditLogRepository,
    cache: ConfigCacheProtocol,
) -> ConfigService:
    """构建配置服务实例。"""
    audit_service = AuditService(audit_repo)
    version_service = VersionService(version_repo, audit_service)
    return ConfigService(config_repo, version_service, audit_service, cache)


@router.get("", response_model=list[ConfigVersionResponse])
async def list_versions(
    config_id: str,
    skip: int = 0,
    limit: int = 100,
    version_repo: VersionRepository = Depends(get_version_repo),
    current_user=Depends(get_current_user),
) -> list[ConfigVersionResponse]:
    """获取配置版本历史。

    Args:
        config_id: 配置 ID
        skip: 跳过记录数
        limit: 限制记录数
        version_repo: 版本 Repository
        current_user: 当前用户

    Returns:
        版本历史列表
    """
    versions = await version_repo.get_versions_by_config(
        config_id, skip=skip, limit=limit
    )
    return [ConfigVersionResponse(**v.model_dump()) for v in versions]


@router.get("/{version_num}", response_model=ConfigVersionResponse)
async def get_version(
    config_id: str,
    version_num: int,
    version_repo: VersionRepository = Depends(get_version_repo),
    current_user=Depends(get_current_user),
) -> ConfigVersionResponse:
    """获取指定版本详情。

    Args:
        config_id: 配置 ID
        version_num: 版本号
        version_repo: 版本 Repository
        current_user: 当前用户

    Returns:
        版本详情

    Raises:
        HTTPException: 如果版本不存在
    """
    version = await version_repo.get_version(config_id, version_num)
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在",
        )
    return ConfigVersionResponse(**version.model_dump())


@router.post("/{version_num}/rollback", status_code=status.HTTP_200_OK)
async def rollback_to_version(
    config_id: str,
    version_num: int,
    config_repo: ConfigRepository = Depends(get_config_repo),
    version_repo: VersionRepository = Depends(get_version_repo),
    audit_repo: AuditLogRepository = Depends(get_audit_repo),
    cache: ConfigCacheProtocol = Depends(get_cache),
    current_user=Depends(get_current_user),
) -> dict:
    """回滚到指定版本。

    通过服务层协调完成完整回滚流程：创建回滚版本记录、更新配置值、
    清除缓存并记录审计日志。

    Args:
        config_id: 配置 ID
        version_num: 目标版本号
        config_repo: 配置 Repository
        version_repo: 版本 Repository
        audit_repo: 审计日志 Repository
        cache: 配置缓存
        current_user: 当前用户

    Returns:
        回滚结果

    Raises:
        HTTPException: 如果配置或版本不存在
    """
    service = _build_config_service(config_repo, version_repo, audit_repo, cache)
    result = await service.rollback_config(config_id, version_num, current_user.id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置或版本不存在",
        )
    return {
        "message": f"已回滚到版本 {version_num}",
        "config_id": config_id,
        "new_version": result.version,
    }


@router.get("/diff/{v1}/to/{v2}")
async def compare_versions(
    config_id: str,
    v1: int,
    v2: int,
    version_repo: VersionRepository = Depends(get_version_repo),
    current_user=Depends(get_current_user),
) -> dict:
    """比较两个版本差异。

    Args:
        config_id: 配置 ID
        v1: 第一个版本号
        v2: 第二个版本号
        version_repo: 版本 Repository
        current_user: 当前用户

    Returns:
        版本差异信息

    Raises:
        HTTPException: 如果任一版本不存在
    """
    version1 = await version_repo.get_version(config_id, v1)
    if version1 is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"版本 {v1} 不存在",
        )

    version2 = await version_repo.get_version(config_id, v2)
    if version2 is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"版本 {v2} 不存在",
        )

    # 比较配置值差异
    value1 = version1.value
    value2 = version2.value

    diff = {
        "config_id": config_id,
        "v1": {"version": v1, "value": value1, "updated_at": str(version1.created_at)},
        "v2": {"version": v2, "value": value2, "updated_at": str(version2.created_at)},
        "changed": value1 != value2,
    }

    return diff
