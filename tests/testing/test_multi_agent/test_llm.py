"""LLM模型提供商测试。

测试LLM模型集成功能。
"""

import pytest
import pytest_asyncio

from taolib.testing.multi_agent.models import (
    ModelConfig,
    ModelProvider,
    ModelStatus,
)
from taolib.testing.multi_agent.llm import ModelRegistry
from taolib.testing.multi_agent.llm.protocols import BaseLLMProvider
from taolib.testing.multi_agent.llm.ollama_provider import OllamaProvider


class TestModelRegistry:
    """测试模型注册表。"""

    def test_get_available_providers(self):
        """测试获取可用提供商。"""
        providers = ModelRegistry.get_available_providers()
        assert isinstance(providers, list)
        # Ollama应该已注册
        assert ModelProvider.OLLAMA in providers

    def test_get_provider_class(self):
        """测试获取提供商类。"""
        provider_class = ModelRegistry.get_provider_class(ModelProvider.OLLAMA)
        assert provider_class == OllamaProvider

    def test_create_provider(self):
        """测试创建提供商实例。"""
        config = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama2",
            base_url="http://localhost:11434",
        )
        provider = ModelRegistry.create_provider(config)
        assert isinstance(provider, BaseLLMProvider)
        assert provider.config.provider == ModelProvider.OLLAMA
        assert provider.config.model_name == "llama2"


class TestOllamaProvider:
    """测试Ollama提供商。"""

    @pytest.fixture
    def ollama_config(self):
        """创建Ollama配置。"""
        return ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama2",
            base_url="http://localhost:11434",
            timeout_seconds=10,
        )

    def test_initialization(self, ollama_config):
        """测试初始化。"""
        provider = OllamaProvider(ollama_config)
        assert provider.config == ollama_config
        assert provider.stats is not None
        assert provider.stats.total_requests == 0

    @pytest.mark.asyncio
    async def test_stats_update_success(self, ollama_config):
        """测试成功统计更新。"""
        provider = OllamaProvider(ollama_config)
        provider._update_stats_success(0.5, 100)

        assert provider.stats.total_requests == 1
        assert provider.stats.successful_requests == 1
        assert provider.stats.total_tokens_used == 100
        assert provider.stats.average_latency_seconds == 0.5

    @pytest.mark.asyncio
    async def test_stats_update_failure(self, ollama_config):
        """测试失败统计更新。"""
        provider = OllamaProvider(ollama_config)
        provider._update_stats_failure()

        assert provider.stats.total_requests == 1
        assert provider.stats.failed_requests == 1
        assert provider.stats.last_error_at is not None


class TestModelConfig:
    """测试模型配置。"""

    def test_default_config(self):
        """测试默认配置。"""
        config = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="test-model",
        )
        assert config.provider == ModelProvider.OLLAMA
        assert config.model_name == "test-model"
        assert config.timeout_seconds == 60
        assert config.max_retries == 3
        assert config.temperature == 0.7
        assert config.weight == 1.0

    def test_custom_config(self):
        """测试自定义配置。"""
        config = ModelConfig(
            provider=ModelProvider.HUGGINGFACE,
            model_name="custom-model",
            base_url="http://custom-url",
            timeout_seconds=120,
            max_retries=5,
            temperature=0.5,
            max_tokens=2048,
            weight=2.0,
        )
        assert config.provider == ModelProvider.HUGGINGFACE
        assert config.model_name == "custom-model"
        assert config.base_url == "http://custom-url"
        assert config.timeout_seconds == 120
        assert config.max_retries == 5
        assert config.temperature == 0.5
        assert config.max_tokens == 2048
        assert config.weight == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
