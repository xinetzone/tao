"""LLM模型数据模型。

定义模型提供商和模型配置的数据模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.testing.multi_agent.models.enums import ModelProvider, ModelStatus, LoadBalanceStrategy


class ModelConfig(BaseModel):
    """模型配置。"""

    provider: ModelProvider = Field(..., description="模型提供商")
    model_name: str = Field(..., description="模型名称")
    base_url: str | None = Field(None, description="API基础URL")
    api_key: str | None = Field(None, description="API密钥(可选)")
    timeout_seconds: int = Field(default=60, ge=10, description="超时时间(秒)")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, description="每分钟请求限制")
    rate_limit_tokens_per_minute: int | None = Field(None, ge=1, description="每分钟Token限制")
    max_concurrent_requests: int = Field(default=5, ge=1, description="最大并发请求数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="默认温度参数")
    max_tokens: int | None = Field(None, ge=1, description="最大Token数")
    weight: float = Field(default=1.0, ge=0.0, description="权重(用于加权负载均衡)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class ModelStats(BaseModel):
    """模型统计信息。"""

    total_requests: int = Field(default=0, ge=0, description="总请求数")
    successful_requests: int = Field(default=0, ge=0, description="成功请求数")
    failed_requests: int = Field(default=0, ge=0, description="失败请求数")
    total_tokens_used: int = Field(default=0, ge=0, description="总使用Token数")
    average_latency_seconds: float = Field(default=0.0, ge=0.0, description="平均延迟(秒)")
    current_concurrent_requests: int = Field(default=0, ge=0, description="当前并发请求数")
    requests_this_minute: int = Field(default=0, ge=0, description="本分钟请求数")
    tokens_this_minute: int = Field(default=0, ge=0, description="本分钟Token数")
    last_health_check_at: datetime | None = Field(None, description="上次健康检查时间")
    last_error_at: datetime | None = Field(None, description="上次错误时间")
    last_error_message: str = Field("", description="上次错误信息")


class ModelInstance(BaseModel):
    """模型实例。"""

    id: str = Field(..., description="模型实例ID")
    config: ModelConfig = Field(..., description="模型配置")
    status: ModelStatus = Field(default=ModelStatus.UNAVAILABLE, description="模型状态")
    stats: ModelStats = Field(default_factory=ModelStats, description="统计信息")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LoadBalanceConfig(BaseModel):
    """负载均衡配置。"""

    strategy: LoadBalanceStrategy = Field(default=LoadBalanceStrategy.ROUND_ROBIN, description="策略")
    fallback_enabled: bool = Field(default=True, description="是否启用降级")
    health_check_interval_seconds: int = Field(default=30, ge=5, description="健康检查间隔(秒)")
    circuit_breaker_enabled: bool = Field(default=True, description="是否启用熔断器")
    circuit_breaker_failure_threshold: int = Field(default=5, ge=1, description="熔断器失败阈值")
    circuit_breaker_reset_timeout_seconds: int = Field(default=60, ge=10, description="熔断器重置超时(秒)")
