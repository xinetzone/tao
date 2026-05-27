"""审计日志数据模型。

定义审计日志相关的 Pydantic 模型和枚举类型。
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuditAction(StrEnum):
    """审计操作类型枚举。"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login.failed"
    EXPORT = "export"
    IMPORT = "import"
    EXECUTE = "execute"
    ACCESS = "access"


class AuditStatus(StrEnum):
    """审计操作状态枚举。"""

    SUCCESS = "success"
    FAILED = "failed"


class AuditLog(BaseModel):
    """审计日志模型。

    记录系统中所有重要操作的审计信息。

    Attributes:
        id: 日志唯一标识符
        timestamp: 操作时间戳
        user_id: 操作用户 ID
        action: 操作类型
        resource_type: 资源类型
        resource_id: 资源 ID
        details: 操作详情
        ip_address: 客户端 IP 地址
        user_agent: 客户端 User-Agent
        status: 操作状态
        error_message: 错误信息（失败时）
    """

    id: UUID = Field(default_factory=uuid4, description="日志唯一标识符")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="操作时间戳"
    )
    user_id: str | None = Field(default=None, description="操作用户 ID")
    action: AuditAction = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型", max_length=100)
    resource_id: str | None = Field(default=None, description="资源 ID")
    details: dict[str, Any] = Field(default_factory=dict, description="操作详情")
    ip_address: str | None = Field(default=None, description="客户端 IP 地址")
    user_agent: str | None = Field(default=None, description="客户端 User-Agent")
    status: AuditStatus = Field(default=AuditStatus.SUCCESS, description="操作状态")
    error_message: str | None = Field(default=None, description="错误信息")

    model_config = {"from_attributes": True}


class AuditLogCreate(BaseModel):
    """创建审计日志请求模型。

    Attributes:
        user_id: 操作用户 ID
        action: 操作类型
        resource_type: 资源类型
        resource_id: 资源 ID
        details: 操作详情
        ip_address: 客户端 IP 地址
        user_agent: 客户端 User-Agent
        status: 操作状态
        error_message: 错误信息
    """

    user_id: str | None = Field(default=None, description="操作用户 ID")
    action: AuditAction = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型", max_length=100)
    resource_id: str | None = Field(default=None, description="资源 ID")
    details: dict[str, Any] = Field(default_factory=dict, description="操作详情")
    ip_address: str | None = Field(default=None, description="客户端 IP 地址")
    user_agent: str | None = Field(default=None, description="客户端 User-Agent")
    status: AuditStatus = Field(default=AuditStatus.SUCCESS, description="操作状态")
    error_message: str | None = Field(default=None, description="错误信息")


class AuditLogResponse(BaseModel):
    """审计日志响应模型。

    Attributes:
        id: 日志唯一标识符
        timestamp: 操作时间戳
        user_id: 操作用户 ID
        action: 操作类型
        resource_type: 资源类型
        resource_id: 资源 ID
        details: 操作详情
        ip_address: 客户端 IP 地址
        user_agent: 客户端 User-Agent
        status: 操作状态
        error_message: 错误信息
    """

    id: UUID = Field(..., description="日志唯一标识符")
    timestamp: datetime = Field(..., description="操作时间戳")
    user_id: str | None = Field(default=None, description="操作用户 ID")
    action: AuditAction = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型")
    resource_id: str | None = Field(default=None, description="资源 ID")
    details: dict[str, Any] = Field(default_factory=dict, description="操作详情")
    ip_address: str | None = Field(default=None, description="客户端 IP 地址")
    user_agent: str | None = Field(default=None, description="客户端 User-Agent")
    status: AuditStatus = Field(..., description="操作状态")
    error_message: str | None = Field(default=None, description="错误信息")

    model_config = {"from_attributes": True}


class AuditLogFilter(BaseModel):
    """审计日志查询过滤器。

    Attributes:
        user_id: 按用户 ID 过滤
        action: 按操作类型过滤
        resource_type: 按资源类型过滤
        resource_id: 按资源 ID 过滤
        status: 按状态过滤
        start_time: 开始时间
        end_time: 结束时间
        ip_address: 按 IP 地址过滤
        limit: 返回数量限制
        offset: 偏移量
    """

    user_id: str | None = Field(default=None, description="按用户 ID 过滤")
    action: AuditAction | None = Field(default=None, description="按操作类型过滤")
    resource_type: str | None = Field(default=None, description="按资源类型过滤")
    resource_id: str | None = Field(default=None, description="按资源 ID 过滤")
    status: AuditStatus | None = Field(default=None, description="按状态过滤")
    start_time: datetime | None = Field(default=None, description="开始时间")
    end_time: datetime | None = Field(default=None, description="结束时间")
    ip_address: str | None = Field(default=None, description="按 IP 地址过滤")
    limit: int = Field(default=100, ge=1, le=1000, description="返回数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")


class AuditLogListResponse(BaseModel):
    """审计日志列表响应模型。

    Attributes:
        items: 日志列表
        total: 总数量
        limit: 每页数量
        offset: 偏移量
    """

    items: list[AuditLogResponse] = Field(default_factory=list, description="日志列表")
    total: int = Field(..., description="总数量")
    limit: int = Field(..., description="每页数量")
    offset: int = Field(..., description="偏移量")


class RequestAuditInfo(BaseModel):
    """请求审计信息。

    用于中间件自动收集请求信息。

    Attributes:
        method: HTTP 方法
        path: 请求路径
        query_params: 查询参数
        path_params: 路径参数
        headers: 请求头（敏感信息已过滤）
        status_code: 响应状态码
        response_time_ms: 响应时间（毫秒）
    """

    method: str = Field(..., description="HTTP 方法")
    path: str = Field(..., description="请求路径")
    query_params: dict[str, str] = Field(default_factory=dict, description="查询参数")
    path_params: dict[str, str] = Field(default_factory=dict, description="路径参数")
    headers: dict[str, str] = Field(default_factory=dict, description="请求头")
    status_code: int | None = Field(default=None, description="响应状态码")
    response_time_ms: float | None = Field(default=None, description="响应时间（毫秒）")
