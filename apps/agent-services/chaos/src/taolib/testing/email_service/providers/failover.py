"""提供商故障转移管理器。

实现多提供商自动故障转移机制，包含简化的电路断路器逻辑。
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from taolib.testing.email_service.errors import AllProvidersFailedError, ProviderError
from taolib.testing.email_service.models.email import EmailDocument

from .protocol import EmailProviderProtocol, ProviderHealthStatus, SendResult

logger = logging.getLogger(__name__)


@dataclass
class _ProviderState:
    """内部提供商状态跟踪。"""

    provider: EmailProviderProtocol
    priority: int
    is_healthy: bool = True
    consecutive_failures: int = 0
    last_failure: datetime | None = None
    cooldown_until: datetime | None = None
    total_sent: int = 0
    total_failed: int = 0


class ProviderFailoverManager:
    """提供商故障转移管理器。

    按优先级排序提供商，自动在主提供商失败时切换到备用提供商。
    每个提供商独立跟踪健康状态，失败超过阈值后进入冷却期。
    """

    def __init__(
        self,
        providers: list[tuple[EmailProviderProtocol, int]],
        max_consecutive_failures: int = 3,
        cooldown_seconds: int = 60,
    ) -> None:
        """初始化。

        Args:
            providers: (提供商实例, 优先级) 列表，优先级数值越小优先级越高
            max_consecutive_failures: 连续失败次数阈值，超过后进入冷却
            cooldown_seconds: 冷却时间（秒）
        """
        self._states: list[_ProviderState] = [
            _ProviderState(provider=p, priority=pri) for p, pri in providers
        ]
        self._states.sort(key=lambda s: s.priority)
        self._max_failures = max_consecutive_failures
        self._cooldown_seconds = cooldown_seconds

    async def send(self, email: EmailDocument) -> SendResult:
        """通过可用提供商发送邮件，自动故障转移。

        Args:
            email: 邮件文档

        Returns:
            发送结果

        Raises:
            AllProvidersFailedError: 所有提供商均失败
        """
        now = datetime.now(UTC)
        errors: list[tuple[str, str]] = []

        available = [
            s
            for s in self._states
            if s.cooldown_until is None or now >= s.cooldown_until
        ]

        if not available:
            raise AllProvidersFailedError(
                [(s.provider.name, "In cooldown") for s in self._states]
            )

        for state in available:
            try:
                result = await state.provider.send(email)
                if result.success:
                    state.consecutive_failures = 0
                    state.is_healthy = True
                    state.total_sent += 1
                    return result
                raise ProviderError(result.error_message or "Send failed")
            except Exception as e:
                error_msg = str(e)
                state.consecutive_failures += 1
                state.total_failed += 1
                state.last_failure = now
                errors.append((state.provider.name, error_msg))

                if state.consecutive_failures >= self._max_failures:
                    state.is_healthy = False
                    state.cooldown_until = datetime.fromtimestamp(
                        now.timestamp() + self._cooldown_seconds, tz=UTC
                    )
                    logger.warning(
                        "Provider %s entered cooldown for %ds after %d failures",
                        state.provider.name,
                        self._cooldown_seconds,
                        state.consecutive_failures,
                    )

        raise AllProvidersFailedError(errors)

    async def send_bulk(self, emails: list[EmailDocument]) -> list[SendResult]:
        """批量发送邮件。

        Args:
            emails: 邮件文档列表

        Returns:
            发送结果列表
        """
        results: list[SendResult] = []
        for email in emails:
            try:
                result = await self.send(email)
                results.append(result)
            except AllProvidersFailedError:
                results.append(
                    SendResult(
                        success=False,
                        provider_name="none",
                        error_message="All providers failed",
                    )
                )
        return results

    async def run_health_checks(self) -> None:
        """运行健康检查，尝试恢复冷却中的提供商。"""
        now = datetime.now(UTC)
        for state in self._states:
            if state.is_healthy:
                continue
            if state.cooldown_until and now < state.cooldown_until:
                continue
            try:
                health = await state.provider.check_health()
                if health.is_healthy:
                    state.is_healthy = True
                    state.consecutive_failures = 0
                    state.cooldown_until = None
                    logger.info("Provider %s recovered", state.provider.name)
            except Exception:
                pass  # 保持不健康状态

    def get_provider_statuses(self) -> list[ProviderHealthStatus]:
        """获取所有提供商状态。

        Returns:
            提供商健康状态列表
        """
        return [
            ProviderHealthStatus(
                provider_name=s.provider.name,
                is_healthy=s.is_healthy,
                consecutive_failures=s.consecutive_failures,
                last_check=s.last_failure,
                last_error=None,
            )
            for s in self._states
        ]


