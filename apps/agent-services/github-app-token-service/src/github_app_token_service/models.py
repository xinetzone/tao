"""Pydantic 数据模型定义。

本模块定义服务对外暴露的 RESTful API 请求与响应模型，
与 taolib 内部模型解耦，便于独立演进。
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TokenStrategy(StrEnum):
    """调用方请求安装令牌时表达的策略意图。"""

    AUTO = "auto"
    ENABLED = "enabled"
    DISABLED = "disabled"


class TokenRequest(BaseModel):
    """获取安装令牌的请求体。"""

    installation_id: str = Field(..., description="GitHub App 安装实例 ID")
    permissions: dict[str, str] = Field(
        default_factory=dict, description="限定令牌能力的权限映射"
    )
    repositories: list[str] = Field(
        default_factory=list, description="限定令牌可访问的仓库列表"
    )
    strategy: TokenStrategy = Field(
        default=TokenStrategy.AUTO, description="令牌策略：auto / enabled / disabled"
    )


class TokenResponse(BaseModel):
    """安装令牌响应结果。"""

    token: str = Field(..., description="安装令牌明文")
    expires_at: datetime = Field(..., description="令牌过期时间（UTC）")
    token_kind: str = Field(..., description="令牌类型：stateful / stateless / unknown")
    requested_strategy: str = Field(..., description="调用方原始请求的策略值")
    effective_strategy: str = Field(..., description="实际生效的策略值")
    degraded: bool = Field(..., description="是否因环境约束发生了策略降级")


class CacheClearResponse(BaseModel):
    """缓存清除响应。"""

    cleared: bool = Field(..., description="是否成功清除")
    message: str = Field(..., description="操作结果说明")


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str = Field(..., description="服务状态")
    github_app_id: str | None = Field(None, description="GitHub App ID（脱敏）")
    environment: str | None = Field(None, description="GitHub 运行环境")
