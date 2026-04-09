"""LLM模型管理器。

统一管理所有LLM模型提供商,提供统一的接口。
"""

from typing import AsyncGenerator, Optional

from taolib.testing.multi_agent.errors import (
    LLMError,
    ModelUnavailableError,
)
from taolib.testing.multi_agent.llm.load_balancer import LoadBalancer
from taolib.testing.multi_agent.llm.protocols import BaseLLMProvider
from taolib.testing.multi_agent.llm.registry import ModelRegistry
from taolib.testing.multi_agent.models import (
    LoadBalanceConfig,
    ModelConfig,
    ModelProvider,
)


class LLMManager:
    """LLM模型管理器。"""

    def __init__(
        self, load_balance_config: Optional[LoadBalanceConfig] = None):
        """初始化LLM管理器。

        Args:
            load_balance_config: 负载均衡配置
        """
        self._load_balancer = LoadBalancer(load_balance_config)
        self._default_provider: Optional[BaseLLMProvider] = None

    def add_model(self, config: ModelConfig, instance_id: Optional[str] = None) -> str:
        """添加一个模型。

        Args:
            config: 模型配置
            instance_id: 实例ID,如果为None则自动生成

        Returns:
            str: 实例ID
        """
        if instance_id is None:
            import uuid
            instance_id = f"{config.provider.value}-{uuid.uuid4().hex[:8]}"

        provider = ModelRegistry.create_provider(config)
        self._load_balancer.register_provider(instance_id, provider)

        if self._default_provider is None:
            self._default_provider = provider

        return instance_id

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        instance_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        """生成文本。

        Args:
            prompt: 用户输入的提示词
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_prompt: 系统提示词
            instance_id: 指定实例ID,如果为None则使用负载均衡选择
            **kwargs: 其他参数

        Returns:
            str: 生成的文本

        Raises:
            ModelUnavailableError: 没有可用的模型
            LLMError: 生成过程出错
        """
        if instance_id is not None:
            # 使用指定实例
            provider = self._load_balancer._providers.get(instance_id)
            if provider is None:
                raise ModelUnavailableError(f"Provider {instance_id} not found")
            selected_id = instance_id
        else:
            # 使用负载均衡选择
            selected_id, provider = self._load_balancer.select_provider()

        try:
            result = await provider.generate(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
                **kwargs,
            )
            self._load_balancer.record_success(selected_id)
            return result
        except Exception as e:
            self._load_balancer.record_failure(selected_id)
            raise LLMError(f"Generation failed: {e}")

    async def generate_stream(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        instance_id: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """流式生成文本。

        Args:
            prompt: 用户输入的提示词
            temperature: 温度参数
            max_tokens: 最大生成token数
            system_prompt: 系统提示词
            instance_id: 指定实例ID,如果为None则使用负载均衡选择
            **kwargs: 其他参数

        Yields:
            str: 生成的文本片段

        Raises:
            ModelUnavailableError: 没有可用的模型
            LLMError: 生成过程出错
        """
        if instance_id is not None:
            # 使用指定实例
            provider = self._load_balancer._providers.get(instance_id)
            if provider is None:
                raise ModelUnavailableError(f"Provider {instance_id} not found")
            selected_id = instance_id
        else:
            # 使用负载均衡选择
            selected_id, provider = self._load_balancer.select_provider()

        try:
            async for chunk in provider.generate_stream(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
                **kwargs,
            ):
                yield chunk
            self._load_balancer.record_success(selected_id)
        except Exception as e:
            self._load_balancer.record_failure(selected_id)
            raise LLMError(f"Stream generation failed: {e}")

    async def health_check(self, instance_id: Optional[str] = None) -> bool:
        """健康检查。

        Args:
            instance_id: 指定实例ID,如果为None则检查所有

        Returns:
            bool: 是否健康
        """
        if instance_id is not None:
            provider = self._load_balancer._providers.get(instance_id)
            if provider is None:
                return False
            return await provider.health_check()
        else:
            await self._load_balancer.health_check_all()
            return len(self._load_balancer.get_available_providers()) > 0

    def get_available_models(self) -> list[str]:
        """获取所有可用的模型实例ID。

        Returns:
            list[str]: 可用的模型实例ID列表
        """
        return [instance_id for instance_id, _ in self._load_balancer.get_available_providers()]

    def get_model_stats(self, instance_id: str):
        """获取模型统计信息。

        Args:
            instance_id: 实例ID

        Returns:
            Optional[ModelInstance]: 模型实例信息
        """
        return self._load_balancer.get_instance_stats(instance_id)

    def get_all_models(self):
        """获取所有模型实例信息。

        Returns:
            list[ModelInstance]: 模型实例列表
        """
        return self._load_balancer.get_all_instances()


# 全局管理器实例
_default_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """获取全局LLM管理器。

    Returns:
        LLMManager: LLM管理器
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = LLMManager()
    return _default_manager


def set_llm_manager(manager: LLMManager) -> None:
    """设置全局LLM管理器。

    Args:
        manager: LLM管理器
    """
    global _default_manager
    _default_manager = manager
