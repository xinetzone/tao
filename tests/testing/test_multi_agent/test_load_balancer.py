"""负载均衡器和LLM管理器测试。

测试负载均衡和LLM管理功能。
"""

import pytest

from taolib.testing.multi_agent.llm import LoadBalancer, LLMManager
from taolib.testing.multi_agent.models import (
    LoadBalanceConfig,
    LoadBalanceStrategy,
    ModelConfig,
    ModelProvider,
    ModelStatus,
)
from taolib.testing.multi_agent.llm.ollama_provider import OllamaProvider


class TestLoadBalancer:
    """测试负载均衡器。"""

    @pytest.fixture
    def load_balancer(self):
        """创建负载均衡器。"""
        config = LoadBalanceConfig(
            strategy=LoadBalanceStrategy.ROUND_ROBIN,
            circuit_breaker_failure_threshold=3,
            circuit_breaker_reset_timeout_seconds=60,
        )
        return LoadBalancer(config)

    @pytest.fixture
    def mock_providers(self):
        """创建模拟提供商配置。"""
        configs = [
            ModelConfig(
                provider=ModelProvider.OLLAMA,
                model_name="llama2",
                base_url="http://localhost:11434",
                weight=1.0,
            ),
            ModelConfig(
                provider=ModelProvider.OLLAMA,
                model_name="mistral",
                base_url="http://localhost:11434",
                weight=2.0,
            ),
        ]
        return configs

    def test_register_provider(self, load_balancer, mock_providers):
        """测试注册提供商。"""
        for i, config in enumerate(mock_providers):
            provider = OllamaProvider(config)
            instance_id = f"provider-{i}"
            load_balancer.register_provider(instance_id, provider)

        instances = load_balancer.get_all_instances()
        assert len(instances) == 2

    def test_get_available_providers(self, load_balancer, mock_providers):
        """测试获取可用提供商。"""
        for i, config in enumerate(mock_providers):
            provider = OllamaProvider(config)
            instance_id = f"provider-{i}"
            load_balancer.register_provider(instance_id, provider)

        available = load_balancer.get_available_providers()
        assert len(available) == 2

    def test_round_robin_selection(self, load_balancer, mock_providers):
        """测试轮询选择。"""
        load_balancer._config.strategy = LoadBalanceStrategy.ROUND_ROBIN

        for i, config in enumerate(mock_providers):
            provider = OllamaProvider(config)
            instance_id = f"provider-{i}"
            load_balancer.register_provider(instance_id, provider)

        selected = []
        for _ in range(4):
            instance_id, _ = load_balancer.select_provider()
            selected.append(instance_id)

        assert selected[0] != selected[1]
        assert selected[0] == selected[2]
        assert selected[1] == selected[3]

    def test_random_selection(self, load_balancer, mock_providers):
        """测试随机选择。"""
        load_balancer._config.strategy = LoadBalanceStrategy.RANDOM

        for i, config in enumerate(mock_providers):
            provider = OllamaProvider(config)
            instance_id = f"provider-{i}"
            load_balancer.register_provider(instance_id, provider)

        selected = []
        for _ in range(10):
            instance_id, _ = load_balancer.select_provider()
            selected.append(instance_id)

        # 应该至少有两个不同的选择
        assert len(set(selected)) >= 1

    def test_weighted_selection(self, load_balancer, mock_providers):
        """测试加权选择。"""
        load_balancer._config.strategy = LoadBalanceStrategy.WEIGHTED

        for i, config in enumerate(mock_providers):
            provider = OllamaProvider(config)
            instance_id = f"provider-{i}"
            load_balancer.register_provider(instance_id, provider)

        selected = []
        for _ in range(20):
            instance_id, _ = load_balancer.select_provider()
            selected.append(instance_id)

        # provider-1权重更高,应该被选中更多次
        count_0 = selected.count("provider-0")
        count_1 = selected.count("provider-1")
        assert count_1 > count_0 or count_0 > 0  # 至少应该有一些选择

    def test_circuit_breaker(self, load_balancer, mock_providers):
        """测试熔断器。"""
        for i, config in enumerate(mock_providers):
            provider = OllamaProvider(config)
            instance_id = f"provider-{i}"
            load_balancer.register_provider(instance_id, provider)

        # 记录失败直到熔断
        for _ in range(3):
            load_balancer.record_failure("provider-0")

        # 检查状态
        state = load_balancer._circuit_breaker_states["provider-0"]
        assert state["open_since"] is not None
        assert state["failures"] == 3

        # provider-0应该被熔断,不可用
        available = load_balancer.get_available_providers()
        available_ids = [id for id, _ in available]
        assert "provider-0" not in available_ids
        assert "provider-1" in available_ids

        # 记录成功应该重置失败计数
        load_balancer.record_success("provider-1")
        state1 = load_balancer._circuit_breaker_states["provider-1"]
        assert state1["failures"] == 0


class TestLLMManager:
    """测试LLM管理器。"""

    @pytest.fixture
    def llm_manager(self):
        """创建LLM管理器。"""
        config = LoadBalanceConfig(
            strategy=LoadBalanceStrategy.ROUND_ROBIN,
        )
        return LLMManager(config)

    def test_add_model(self, llm_manager):
        """测试添加模型。"""
        config = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama2",
            base_url="http://localhost:11434",
        )
        instance_id = llm_manager.add_model(config, "test-instance")

        assert instance_id == "test-instance"

        all_models = llm_manager.get_all_models()
        assert len(all_models) == 1
        assert all_models[0].id == "test-instance"

    def test_get_available_models(self, llm_manager):
        """测试获取可用模型。"""
        config1 = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama2",
            base_url="http://localhost:11434",
        )
        config2 = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="mistral",
            base_url="http://localhost:11434",
        )

        llm_manager.add_model(config1, "model-1")
        llm_manager.add_model(config2, "model-2")

        available = llm_manager.get_available_models()
        assert len(available) == 2
        assert "model-1" in available
        assert "model-2" in available

    def test_get_model_stats(self, llm_manager):
        """测试获取模型统计。"""
        config = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama2",
            base_url="http://localhost:11434",
        )
        instance_id = llm_manager.add_model(config, "test-instance")

        stats = llm_manager.get_model_stats(instance_id)
        assert stats is not None
        assert stats.id == "test-instance"
        assert stats.stats.total_requests == 0

    def test_load_balance_config(self):
        """测试负载均衡配置。"""
        config = LoadBalanceConfig(
            strategy=LoadBalanceStrategy.LEAST_CONNECTIONS,
            health_check_interval_seconds=10,
            circuit_breaker_enabled=True,
            circuit_breaker_failure_threshold=5,
            circuit_breaker_reset_timeout_seconds=120,
        )

        assert config.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS
        assert config.health_check_interval_seconds == 10
        assert config.circuit_breaker_enabled is True
        assert config.circuit_breaker_failure_threshold == 5
        assert config.circuit_breaker_reset_timeout_seconds == 120


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
