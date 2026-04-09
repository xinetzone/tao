"""LLM模型协议接口。

定义所有LLM模型提供商必须实现的统一接口。
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Protocol, runtime_checkable

from taolib.testing.multi_agent.models import ModelConfig, ModelStats


@runtime_checkable
class LLMProvider(Protocol):
    """LLM模型提供商协议。"""

    @property
    def config(self) -> ModelConfig:
        """获取模型配置。"""
        ...

    @property
    def stats(self) -> ModelStats:
        """获取模型统计信息。"""
        ...

    async def health_check(self) -> bool:
        """检查模型是否健康可用。

        Returns:
            bool: 模型是否健康可用
        """
        ...

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs,
    ) -> str:
        """同步生成文本。

        Args:
            prompt: 用户输入的提示词
            temperature: 温度参数,如果为None则使用默认配置
            max_tokens: 最大生成token数,如果为None则使用默认配置
            system_prompt: 系统提示词,如果为None则使用默认配置
            **kwargs: 其他模型特定参数

        Returns:
            str: 生成的文本

        Raises:
            LLMError: 生成过程中出错
        """
        ...

    async def generate_stream(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """流式生成文本。

        Args:
            prompt: 用户输入的提示词
            temperature: 温度参数,如果为None则使用默认配置
            max_tokens: 最大生成token数,如果为None则使用默认配置
            system_prompt: 系统提示词,如果为None则使用默认配置
            **kwargs: 其他模型特定参数

        Yields:
            str: 生成的文本片段

        Raises:
            LLMError: 生成过程中出错
        """
        ...


class BaseLLMProvider(ABC):
    """LLM模型提供商基类。"""

    def __init__(self, config: ModelConfig):
        """初始化模型提供商。

        Args:
            config: 模型配置
        """
        self._config = config
        self._stats = ModelStats()

    @property
    def config(self) -> ModelConfig:
        """获取模型配置。"""
        return self._config

    @property
    def stats(self) -> ModelStats:
        """获取模型统计信息。"""
        return self._stats

    @abstractmethod
    async def health_check(self) -> bool:
        """检查模型是否健康可用。"""
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs,
    ) -> str:
        """同步生成文本。"""
        ...

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """流式生成文本。"""
        ...

    def _update_stats_success(self, latency_seconds: float, tokens_used: int = 0) -> None:
        """更新成功请求的统计信息。

        Args:
            latency_seconds: 请求延迟(秒)
            tokens_used: 使用的token数
        """
        self._stats.total_requests += 1
        self._stats.successful_requests += 1
        self._stats.total_tokens_used += tokens_used

        total_successful = self._stats.successful_requests
        if total_successful > 0:
            prev_avg = self._stats.average_latency_seconds
            self._stats.average_latency_seconds = (
                prev_avg * (total_successful - 1) + latency_seconds
            ) / total_successful

    def _update_stats_failure(self) -> None:
        """更新失败请求的统计信息。"""
        from datetime import UTC, datetime

        self._stats.total_requests += 1
        self._stats.failed_requests += 1
        self._stats.last_error_at = datetime.now(UTC)
