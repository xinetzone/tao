"""LLM模型注册表。

管理和注册所有可用的LLM模型提供商。
"""

from typing import Type

from taolib.testing.multi_agent.llm.protocols import BaseLLMProvider
from taolib.testing.multi_agent.models import ModelConfig, ModelProvider


class ModelRegistry:
    """LLM模型注册表。"""

    _providers: dict[ModelProvider, Type[BaseLLMProvider]] = {}

    @classmethod
    def register(cls, provider_type: ModelProvider, provider_class: Type[BaseLLMProvider]) -> None:
        """注册模型提供商。

        Args:
            provider_type: 模型提供商类型
            provider_class: 提供商类
        """
        cls._providers[provider_type] = provider_class

    @classmethod
    def get_provider_class(cls, provider_type: ModelProvider) -> Type[BaseLLMProvider]:
        """获取模型提供商类。

        Args:
            provider_type: 模型提供商类型

        Returns:
            Type[BaseLLMProvider]: 提供商类

        Raises:
            ValueError: 提供商未注册
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Provider {provider_type} not registered")
        return cls._providers[provider_type]

    @classmethod
    def create_provider(cls, config: ModelConfig) -> BaseLLMProvider:
        """创建模型提供商实例。

        Args:
            config: 模型配置

        Returns:
            BaseLLMProvider: 提供商实例
        """
        provider_class = cls.get_provider_class(config.provider)
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> list[ModelProvider]:
        """获取所有已注册的提供商。

        Returns:
            list[ModelProvider]: 提供商列表
        """
        return list(cls._providers.keys())


# 尝试注册提供商
try:
    from taolib.testing.multi_agent.llm.ollama_provider import OllamaProvider
    ModelRegistry.register(ModelProvider.OLLAMA, OllamaProvider)
except ImportError:
    pass
