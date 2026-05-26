"""Pydantic models for rate limiter configuration, responses, and documents."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# ============================================================================
# Configuration Models
# ============================================================================


class PathRule(BaseModel):
    """路径级限流规则。"""

    limit: int = Field(..., ge=1, description="请求上限")
    window_seconds: int | None = Field(None, ge=1, description="滑动窗口大小（秒）")
    description: str = Field("", description="规则描述")
    methods: list[str] | None = Field(None, description="适用的 HTTP 方法（None=全部）")


class WhitelistConfig(BaseModel):
    """白名单配置。"""

    ips: list[str] = Field(default_factory=list, description="白名单 IP 列表")
    user_ids: list[str] = Field(default_factory=list, description="白名单用户 ID 列表")
    bypass_paths: list[str] = Field(default_factory=list, description="不受限流的路径")


class RateLimitConfig(BaseModel):
    """限流配置。"""

    enabled: bool = Field(True, description="是否启用限流")
    default_limit: int = Field(100, ge=1, description="默认每分钟请求数")
    window_seconds: int = Field(60, ge=1, description="滑动窗口大小（秒）")
    path_rules: dict[str, PathRule] = Field(
        default_factory=dict, description="路径级覆盖规则"
    )
    whitelist: WhitelistConfig = Field(
        default_factory=WhitelistConfig, description="白名单配置"
    )
    redis_url: str = Field("redis://localhost:6379/1", description="Redis 连接 URL")
    mongo_violation_ttl_days: int = Field(90, ge=1, description="违规记录 TTL（天）")
    mongo_collection: str = Field("rate_limit_violations", description="违规记录集合名")

    @classmethod
    def from_toml(cls, config_path: str) -> RateLimitConfig:
        """从 TOML 文件加载配置。

        Args:
            config_path: TOML 配置文件路径

        Returns:
            限流配置实例
        """
        import tomllib
        from pathlib import Path

        path = Path(config_path)
        if not path.exists():
            # Return default config if file doesn't exist
            return cls()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        rate_limit_data = data.get("rate_limit", {})
        return cls(**rate_limit_data)


# ============================================================================
# Rate Limit Check Result
# ============================================================================


class RateLimitResult(BaseModel):
    """限流检查结果。"""

    allowed: bool = Field(..., description="是否允许请求")
    limit: int = Field(..., description="限流阈值")
    remaining: int = Field(..., ge=0, description="剩余请求数")
    reset_timestamp: float = Field(..., description="窗口重置时间戳")
    retry_after: int | None = Field(
        None, ge=0, description="建议重试秒数（仅被限流时）"
    )


# ============================================================================
# Response Models
# ============================================================================


class RateLimitErrorResponse(BaseModel):
    """429 响应体。"""

    error: str = Field("rate_limit_exceeded")
    message: str = Field("请求过于频繁，请稍后重试")
    retry_after: int = Field(..., description="建议重试秒数")
    limit: int = Field(..., description="限流阈值")
    window_seconds: int = Field(..., description="窗口大小")


class TopUserEntry(BaseModel):
    """Top Users 统计条目。"""

    identifier: str
    request_count: int
    identifier_type: str


class ViolationStatsEntry(BaseModel):
    """违规统计条目。"""

    identifier: str
    count: int
    identifier_type: str
    last_violation: datetime | None = None


class RealtimeStats(BaseModel):
    """实时请求统计。"""

    active_requests: int = Field(0, description="当前活跃请求数")
    requests_per_second: float = Field(0.0, description="每秒请求数")
    top_paths: list[dict[str, Any]] = Field(
        default_factory=list, description="热门路径"
    )


# ============================================================================
# MongoDB Document Models
# ============================================================================


class ViolationDocument(BaseModel):
    """MongoDB 限流违规文档模型。"""

    id: str = Field(default="", alias="_id")
    identifier: str = Field(..., description="标识符: user:{id} 或 ip:{addr}")
    identifier_type: Literal["user", "ip"] = Field(..., description="标识符类型")
    user_id: str | None = Field(default=None, description="用户 ID")
    ip_address: str = Field(..., max_length=45, description="IP 地址")
    path: str = Field(..., description="请求路径")
    method: str = Field(..., description="HTTP 方法")
    request_count: int = Field(..., description="窗口内请求数")
    limit: int = Field(..., description="限流阈值")
    window_seconds: int = Field(..., description="窗口大小")
    retry_after: int = Field(..., description="建议重试秒数")
    user_agent: str | None = Field(default=None, description="User-Agent")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="违规时间"
    )

    model_config = {"populate_by_name": True}

    def to_mongo_dict(self) -> dict[str, Any]:
        """转换为 MongoDB 插入字典。"""
        data = self.model_dump(by_alias=True, exclude={"id"})
        if not data.get("_id"):
            from bson import ObjectId

            data["_id"] = str(ObjectId())
        return data


