"""配置管理 API 模块。

实现配置 CRUD 的 RESTful API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from ...cache.config_cache import ConfigCacheProtocol
from ...events.publisher import EventPublisher
from ...models.config import ConfigCreate, ConfigResponse, ConfigUpdate
from ...models.user import UserDocument
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
    get_event_publisher,
    get_version_repo,
)

router = APIRouter(prefix="/configs", tags=["配置管理"])

CONFIGS_API_DESCRIPTION = """
配置管理 API 提供配置项的完整生命周期管理，包括创建、查询、更新、删除和发布操作。

## 功能特性

- **环境隔离**：支持多环境配置管理（development、staging、production）
- **版本控制**：每次修改自动创建版本记录，支持版本回滚
- **审计日志**：记录所有配置变更操作
- **实时推送**：配置发布后通过 WebSocket 实时推送到客户端

## 权限要求

所有端点需要 JWT 认证，部分操作需要特定权限：
- `config:read`：查看配置
- `config:write`：创建/更新配置
- `config:delete`：删除配置
- `config:publish`：发布配置
"""


def _build_config_service(
    config_repo: ConfigRepository,
    version_repo: VersionRepository,
    audit_repo: AuditLogRepository,
    cache: ConfigCacheProtocol,
    event_publisher: EventPublisher | None = None,
) -> ConfigService:
    """构建配置服务实例。"""
    audit_service = AuditService(audit_repo)
    version_service = VersionService(version_repo, audit_service)
    return ConfigService(
        config_repo, version_service, audit_service, cache, event_publisher
    )


@router.get(
    "",
    response_model=list[ConfigResponse],
    summary="获取配置列表",
    description="""
获取配置列表，支持按环境和服务过滤。

## 请求示例

```
GET /configs?environment=production&service=user-service&skip=0&limit=50
```

## 响应示例

```json
[
  {
    "id": "cfg_abc123",
    "key": "database.url",
    "value": "postgresql://localhost:5432/mydb",
    "environment": "production",
    "service": "user-service",
    "status": "published",
    "version": 3,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T14:20:00Z"
  }
]
```
""",
    responses={
        200: {
            "description": "成功获取配置列表",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "cfg_abc123",
                            "key": "database.url",
                            "value": "postgresql://localhost:5432/mydb",
                            "environment": "production",
                            "service": "user-service",
                            "status": "published",
                            "version": 3,
                        }
                    ]
                }
            },
        },
        401: {"description": "未授权 - 缺少或无效的认证令牌"},
    },
)
async def list_configs(
    environment: str | None = Query(default=None, description="环境过滤（development/staging/production）"),
    service: str | None = Query(default=None, description="服务名称过滤"),
    skip: int = Query(default=0, ge=0, description="跳过记录数"),
    limit: int = Query(default=100, ge=1, le=1000, description="返回记录数限制"),
    current_user: UserDocument = Depends(get_current_user),
    config_repo: ConfigRepository = Depends(get_config_repo),
):
    """获取配置列表。"""
    configs = await config_repo.list(
        filters={"environment": environment, "service": service}
        if environment or service
        else None,
        skip=skip,
        limit=limit,
    )
    return [c.to_response() for c in configs]


@router.get(
    "/{config_id}",
    response_model=ConfigResponse,
    summary="获取配置详情",
    description="""
根据 ID 获取单个配置的详细信息。

## 路径参数

- `config_id`: 配置唯一标识符

## 响应示例

```json
{
  "id": "cfg_abc123",
  "key": "database.url",
  "value": "postgresql://localhost:5432/mydb",
  "environment": "production",
  "service": "user-service",
  "status": "published",
  "version": 3,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z",
  "created_by": "user_001",
  "updated_by": "user_002"
}
```
""",
    responses={
        200: {"description": "成功获取配置详情"},
        401: {"description": "未授权"},
        404: {"description": "配置不存在"},
    },
)
async def get_config(
    config_id: str,
    current_user: UserDocument = Depends(get_current_user),
    config_repo: ConfigRepository = Depends(get_config_repo),
):
    """获取配置详情。"""
    config = await config_repo.get_by_id(config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config.to_response()


@router.post(
    "",
    response_model=ConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建配置",
    description="""
创建新的配置项。

## 请求体示例

```json
{
  "key": "api.timeout",
  "value": "30",
  "value_type": "integer",
  "environment": "production",
  "service": "api-gateway",
  "description": "API 请求超时时间（秒）",
  "tags": ["performance", "timeout"]
}
```

## 业务规则

- 配置键在相同环境和服务下必须唯一
- 创建后自动生成版本 1
- 初始状态为 `draft`
""",
    responses={
        201: {"description": "配置创建成功"},
        400: {"description": "请求参数错误或配置键已存在"},
        401: {"description": "未授权"},
        403: {"description": "权限不足"},
    },
)
async def create_config(
    data: ConfigCreate,
    request: Request,
    current_user: UserDocument = Depends(get_current_user),
    config_repo: ConfigRepository = Depends(get_config_repo),
    version_repo: VersionRepository = Depends(get_version_repo),
    audit_repo: AuditLogRepository = Depends(get_audit_repo),
    cache: ConfigCacheProtocol = Depends(get_cache),
    event_publisher: EventPublisher | None = Depends(get_event_publisher),
):
    """创建配置。"""
    service = _build_config_service(
        config_repo, version_repo, audit_repo, cache, event_publisher
    )
    return await service.create_config(data, current_user.id)


@router.put(
    "/{config_id}",
    response_model=ConfigResponse,
    summary="更新配置",
    description="""
更新现有配置项的值或属性。

## 请求体示例

```json
{
  "value": "60",
  "description": "API 请求超时时间（秒）- 已调整"
}
```

## 业务规则

- 更新会自动创建新版本
- 已发布的配置更新后状态变为 `draft`
- 更新操作会记录审计日志
""",
    responses={
        200: {"description": "配置更新成功"},
        400: {"description": "请求参数错误"},
        401: {"description": "未授权"},
        403: {"description": "权限不足"},
        404: {"description": "配置不存在"},
    },
)
async def update_config(
    config_id: str,
    data: ConfigUpdate,
    request: Request,
    current_user: UserDocument = Depends(get_current_user),
    config_repo: ConfigRepository = Depends(get_config_repo),
    version_repo: VersionRepository = Depends(get_version_repo),
    audit_repo: AuditLogRepository = Depends(get_audit_repo),
    cache: ConfigCacheProtocol = Depends(get_cache),
    event_publisher: EventPublisher | None = Depends(get_event_publisher),
):
    """更新配置。"""
    service = _build_config_service(
        config_repo, version_repo, audit_repo, cache, event_publisher
    )
    config = await service.update_config(config_id, data, current_user.id)
    if config is None:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


@router.delete(
    "/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除配置",
    description="""
删除指定的配置项。

## 警告

- 删除操作不可恢复
- 所有历史版本将被删除
- 相关的审计日志将保留
- 如果配置已发布，删除后会推送删除事件

## 权限要求

需要 `config:delete` 权限。
""",
    responses={
        204: {"description": "配置删除成功"},
        401: {"description": "未授权"},
        403: {"description": "权限不足"},
        404: {"description": "配置不存在"},
    },
)
async def delete_config(
    config_id: str,
    request: Request,
    current_user: UserDocument = Depends(get_current_user),
    config_repo: ConfigRepository = Depends(get_config_repo),
    version_repo: VersionRepository = Depends(get_version_repo),
    audit_repo: AuditLogRepository = Depends(get_audit_repo),
    cache: ConfigCacheProtocol = Depends(get_cache),
    event_publisher: EventPublisher | None = Depends(get_event_publisher),
):
    """删除配置。"""
    service = _build_config_service(
        config_repo, version_repo, audit_repo, cache, event_publisher
    )
    deleted = await service.delete_config(config_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="配置不存在")


@router.post(
    "/{config_id}/publish",
    response_model=ConfigResponse,
    summary="发布配置",
    description="""
将配置从草稿状态发布到生产环境。

## 发布流程

1. 验证配置状态为 `draft`
2. 更新状态为 `published`
3. 清除相关缓存
4. 通过 WebSocket 推送变更事件
5. 记录审计日志

## 响应示例

```json
{
  "id": "cfg_abc123",
  "status": "published",
  "version": 4,
  "published_at": "2024-01-15T15:00:00Z",
  "published_by": "user_002"
}
```
""",
    responses={
        200: {"description": "配置发布成功"},
        400: {"description": "配置状态不允许发布"},
        401: {"description": "未授权"},
        403: {"description": "权限不足 - 需要 config:publish 权限"},
        404: {"description": "配置不存在"},
    },
)
async def publish_config(
    config_id: str,
    request: Request,
    current_user: UserDocument = Depends(get_current_user),
    config_repo: ConfigRepository = Depends(get_config_repo),
    version_repo: VersionRepository = Depends(get_version_repo),
    audit_repo: AuditLogRepository = Depends(get_audit_repo),
    cache: ConfigCacheProtocol = Depends(get_cache),
    event_publisher: EventPublisher | None = Depends(get_event_publisher),
):
    """发布配置。"""
    service = _build_config_service(
        config_repo, version_repo, audit_repo, cache, event_publisher
    )
    config = await service.publish_config(config_id, current_user.id)
    if config is None:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


