"""LLM模型负载均衡器。

实现模型自动选择与负载均衡机制。
"""

import random
import time
from datetime import UTC, datetime
from typing import Optional

from taolib.testing.multi_agent.errors import ModelUnavailableError
from taolib.testing.multi_agent.llm.protocols import BaseLLMProvider
from taolib.testing.multi_agent.models import (
    LoadBalanceConfig,
    LoadBalanceStrategy,
    ModelInstance,
    ModelStatus,
)


class LoadBalancer:
    """LLM模型负载均衡器。"""

    def __init__(self, config: Optional[LoadBalanceConfig] = None):
        """初始化负载均衡器。

        Args:
            config: 负载均衡配置
        """
        self._config = config or LoadBalanceConfig()
        self._providers: dict[str, BaseLLMProvider] = {}
        self._instances: dict[str, ModelInstance] = {}
        self._round_robin_index = 0
        self._circuit_breaker_states: dict[str, dict] = {}

    def register_provider(self, instance_id: str, provider: BaseLLMProvider) -> None:
        """注册模型提供商。

        Args:
            instance_id: 实例ID
            provider: 模型提供商实例
        """
        self._providers[instance_id] = provider
        self._instances[instance_id] = ModelInstance(
            id=instance_id,
            config=provider.config,
            status=ModelStatus.AVAILABLE,
        )
        self._circuit_breaker_states[instance_id] = {
            "failures": 0,
            "open_since": None,
        }

    def get_available_providers(self) -> list[tuple[str, BaseLLMProvider]]:
        """获取所有可用的提供商。

        Returns:
            list[tuple[str, BaseLLMProvider]]: 可用的提供商列表
        """
        available = []
        for instance_id, provider in self._providers.items():
            instance = self._instances[instance_id]
            state = self._circuit_breaker_states[instance_id]

            # 检查熔断器状态
            if state["open_since"] is not None:
                elapsed = (datetime.now(UTC) - state["open_since"]).total_seconds()
                if elapsed < self._config.circuit_breaker_reset_timeout_seconds:
                    continue
                # 重置熔断器
                state["open_since"] = None
                state["failures"] = 0

            available.append((instance_id, provider))
        return available

    def _select_round_robin(self, available: list[tuple[str, BaseLLMProvider]]) -> tuple[str, BaseLLMProvider]:
        """轮询策略选择。

        Args:
            available: 可用提供商列表

        Returns:
            tuple[str, BaseLLMProvider]: 选中的提供商
        """
        if not available:
            raise ModelUnavailableError("No available providers")

        selected = available[self._round_robin_index % len(available)]
        self._round_robin_index += 1
        return selected

    def _select_least_connections(self, available: list[tuple[str, BaseLLMProvider]]) -> tuple[str, BaseLLMProvider]:
        """最少连接策略选择。

        Args:
            available: 可用提供商列表

        Returns:
            tuple[str, BaseLLMProvider]: 选中的提供商
        """
        if not available:
            raise ModelUnavailableError("No available providers")

        def get_concurrent(item: tuple[str, BaseLLMProvider]) -> int:
            instance_id, _ = item
            instance = self._instances[instance_id]
            return instance.stats.current_concurrent_requests

        return min(available, key=get_concurrent)

    def _select_random(self, available: list[tuple[str, BaseLLMProvider]]) -> tuple[str, BaseLLMProvider]:
        """随机策略选择。

        Args:
            available: 可用提供商列表

        Returns:
            tuple[str, BaseLLMProvider]: 选中的提供商
        """
        if not available:
            raise ModelUnavailableError("No available providers")
        return random.choice(available)

    def _select_weighted(self, available: list[tuple[str, BaseLLMProvider]]) -> tuple[str, BaseLLMProvider]:
        """加权随机策略选择。

        Args:
            available: 可用提供商列表

        Returns:
            tuple[str, BaseLLMProvider]: 选中的提供商
        """
        if not available:
            raise ModelUnavailableError("No available providers")

        weights = []
        for instance_id, _ in available:
            config = self._instances[instance_id].config
            weights.append(config.weight)

        total_weight = sum(weights)
        if total_weight <= 0:
            return random.choice(available)

        r = random.uniform(0, total_weight)
        cumulative = 0.0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return available[i]

        return available[-1]

    def select_provider(self) -> tuple[str, BaseLLMProvider]:
        """选择一个提供商。

        Returns:
            tuple[str, BaseLLMProvider]: 选中的实例ID和提供商

        Raises:
            ModelUnavailableError: 没有可用的提供商
        """
        available = self.get_available_providers()

        if not available:
            raise ModelUnavailableError("No available providers")

        strategy = self._config.strategy

        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._select_round_robin(available)
        elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._select_least_connections(available)
        elif strategy == LoadBalanceStrategy.RANDOM:
            return self._select_random(available)
        elif strategy == LoadBalanceStrategy.WEIGHTED:
            return self._select_weighted(available)
        else:
            return self._select_round_robin(available)

    def record_success(self, instance_id: str) -> None:
        """记录成功请求。

        Args:
            instance_id: 实例ID
        """
        if instance_id in self._circuit_breaker_states:
            self._circuit_breaker_states[instance_id]["failures"] = 0

    def record_failure(self, instance_id: str) -> None:
        """记录失败请求。

        Args:
            instance_id: 实例ID
        """
        if instance_id not in self._circuit_breaker_states:
            return

        state = self._circuit_breaker_states[instance_id]
        state["failures"] += 1

        if state["failures"] >= self._config.circuit_breaker_failure_threshold:
            state["open_since"] = datetime.now(UTC)

    async def health_check_all(self) -> None:
        """对所有提供商进行健康检查。"""
        for instance_id, provider in self._providers.items():
            is_healthy = await provider.health_check()
            instance = self._instances[instance_id]

            if is_healthy:
                instance.status = ModelStatus.AVAILABLE
            else:
                instance.status = ModelStatus.UNAVAILABLE

    def get_instance_stats(self, instance_id: str) -> Optional[ModelInstance]:
        """获取实例统计信息。

        Args:
            instance_id: 实例ID

        Returns:
            Optional[ModelInstance]: 实例信息
        """
        return self._instances.get(instance_id)

    def get_all_instances(self) -> list[ModelInstance]:
        """获取所有实例信息。

        Returns:
            list[ModelInstance]: 实例列表
        """
        return list(self._instances.values())

    def get_provider(self, instance_id: str) -> Optional[BaseLLMProvider]:
        """获取指定实例ID的提供商。

        Args:
            instance_id: 实例ID

        Returns:
            Optional[BaseLLMProvider]: 提供商实例，如果不存在则返回None
        """
        return self._providers.get(instance_id)
