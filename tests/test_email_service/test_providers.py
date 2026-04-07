"""提供商故障转移测试。"""

import pytest

from taolib.email_service.errors import AllProvidersFailedError
from taolib.email_service.providers.failover import ProviderFailoverManager

from .conftest import MockProvider


class TestProviderFailoverManager:
    @pytest.mark.asyncio
    async def test_send_success_primary(self, sample_email_document):
        primary = MockProvider("primary")
        backup = MockProvider("backup")
        manager = ProviderFailoverManager([(primary, 1), (backup, 2)])

        result = await manager.send(sample_email_document)
        assert result.success
        assert result.provider_name == "primary"

    @pytest.mark.asyncio
    async def test_failover_to_backup(self, sample_email_document):
        primary = MockProvider("primary", should_fail=True)
        backup = MockProvider("backup")
        manager = ProviderFailoverManager([(primary, 1), (backup, 2)])

        result = await manager.send(sample_email_document)
        assert result.success
        assert result.provider_name == "backup"

    @pytest.mark.asyncio
    async def test_all_providers_fail(self, sample_email_document):
        p1 = MockProvider("p1", should_fail=True)
        p2 = MockProvider("p2", should_fail=True)
        manager = ProviderFailoverManager([(p1, 1), (p2, 2)])

        with pytest.raises(AllProvidersFailedError):
            await manager.send(sample_email_document)

    @pytest.mark.asyncio
    async def test_cooldown_after_max_failures(self, sample_email_document):
        failing = MockProvider("failing", should_fail=True)
        backup = MockProvider("backup")
        manager = ProviderFailoverManager(
            [(failing, 1), (backup, 2)],
            max_consecutive_failures=2,
            cooldown_seconds=60,
        )

        # 第一次：failing 失败，backup 成功
        result = await manager.send(sample_email_document)
        assert result.provider_name == "backup"

        # 第二次：failing 失败，backup 成功 → failing 进入冷却
        result = await manager.send(sample_email_document)
        assert result.provider_name == "backup"

        # 第三次：failing 被跳过（冷却中），直接 backup
        result = await manager.send(sample_email_document)
        assert result.success
        assert result.provider_name == "backup"

    @pytest.mark.asyncio
    async def test_get_provider_statuses(self):
        p1 = MockProvider("sendgrid")
        p2 = MockProvider("mailgun")
        manager = ProviderFailoverManager([(p1, 1), (p2, 2)])

        statuses = manager.get_provider_statuses()
        assert len(statuses) == 2
        assert statuses[0].provider_name == "sendgrid"
        assert statuses[0].is_healthy

    @pytest.mark.asyncio
    async def test_send_bulk(self, sample_email_document):
        provider = MockProvider("primary")
        manager = ProviderFailoverManager([(provider, 1)])

        results = await manager.send_bulk(
            [sample_email_document, sample_email_document]
        )
        assert len(results) == 2
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_health_check_recovery(self, sample_email_document):
        provider = MockProvider("recover", should_fail=True)
        manager = ProviderFailoverManager(
            [(provider, 1)],
            max_consecutive_failures=1,
            cooldown_seconds=0,
        )

        # 触发冷却
        with pytest.raises(AllProvidersFailedError):
            await manager.send(sample_email_document)

        # 恢复提供商
        provider._should_fail = False

        # 运行健康检查
        await manager.run_health_checks()

        # 现在应该能成功
        result = await manager.send(sample_email_document)
        assert result.success
