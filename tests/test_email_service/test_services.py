"""服务层测试。"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.email_service.errors import TemplateNotFoundError
from taolib.email_service.models.enums import (
    EmailStatus,
    SubscriptionStatus,
    TrackingEventType,
)
from taolib.email_service.providers.failover import ProviderFailoverManager
from taolib.email_service.queue.memory_queue import InMemoryEmailQueue
from taolib.email_service.repository.email_repo import EmailRepository
from taolib.email_service.repository.subscription_repo import SubscriptionRepository
from taolib.email_service.repository.template_repo import TemplateRepository
from taolib.email_service.repository.tracking_repo import TrackingRepository
from taolib.email_service.services.email_service import EmailService
from taolib.email_service.services.subscription_service import SubscriptionService
from taolib.email_service.services.template_service import TemplateService
from taolib.email_service.services.tracking_service import TrackingService
from taolib.email_service.template.engine import TemplateEngine

from .conftest import MockMongoCollection, MockProvider


class TestTemplateService:
    @pytest.mark.asyncio
    async def test_create_template(self, sample_template_create):
        collection = MockMongoCollection()
        collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="tmpl-new")
        )
        repo = TemplateRepository(collection)
        engine = TemplateEngine()
        service = TemplateService(repo, engine)

        result = await service.create_template(sample_template_create)
        assert result.name == "welcome"
        collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_render_template_not_found(self):
        collection = MockMongoCollection()
        collection.find_one = AsyncMock(return_value=None)
        repo = TemplateRepository(collection)
        engine = TemplateEngine()
        service = TemplateService(repo, engine)

        with pytest.raises(TemplateNotFoundError):
            await service.render_template("nonexistent", {"name": "test"})


class TestSubscriptionService:
    @pytest.mark.asyncio
    async def test_get_or_create_new(self):
        collection = MockMongoCollection()
        collection.find_one = AsyncMock(return_value=None)
        collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="sub-new"))
        repo = SubscriptionRepository(collection)
        service = SubscriptionService(repo)

        result = await service.get_or_create_subscription("new@example.com")
        assert result.email == "new@example.com"
        assert result.status == SubscriptionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_is_subscribed_no_record(self):
        collection = MockMongoCollection()
        collection.find_one = AsyncMock(return_value=None)
        repo = SubscriptionRepository(collection)
        service = SubscriptionService(repo)

        # 无记录视为已订阅
        assert await service.is_subscribed("unknown@example.com") is True


class TestTrackingService:
    @pytest.mark.asyncio
    async def test_record_event(self):
        tracking_collection = MockMongoCollection()
        tracking_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="evt-1")
        )
        email_collection = MockMongoCollection()

        tracking_repo = TrackingRepository(tracking_collection)
        email_repo = EmailRepository(email_collection)
        service = TrackingService(tracking_repo, email_repo)

        result = await service.record_event(
            email_id="email-1",
            event_type=TrackingEventType.DELIVERED,
            recipient="user@example.com",
            provider="sendgrid",
        )
        assert result.email_id == "email-1"
        assert result.event_type == TrackingEventType.DELIVERED

    @pytest.mark.asyncio
    async def test_get_analytics(self):
        collection = MockMongoCollection()
        # Mock 聚合结果 — 使用真正的异步迭代器
        results = [
            {"_id": "sent", "count": 100},
            {"_id": "delivered", "count": 90},
            {"_id": "opened", "count": 40},
            {"_id": "clicked", "count": 10},
            {"_id": "bounced", "count": 5},
        ]

        class _AsyncIter:
            def __init__(self, items):
                self._items = iter(items)

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    return next(self._items)
                except StopIteration:
                    raise StopAsyncIteration

        collection.aggregate = MagicMock(return_value=_AsyncIter(results))

        email_collection = MockMongoCollection()
        tracking_repo = TrackingRepository(collection)
        email_repo = EmailRepository(email_collection)
        service = TrackingService(tracking_repo, email_repo)

        now = datetime.now(UTC)
        analytics = await service.get_analytics(now, now)
        assert analytics.total_sent == 100
        assert analytics.total_delivered == 90
        assert analytics.open_rate == pytest.approx(44.44, rel=0.1)


class TestEmailService:
    def _build_service(self):
        email_collection = MockMongoCollection()
        email_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="email-new")
        )

        template_collection = MockMongoCollection()
        tracking_collection = MockMongoCollection()
        tracking_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="evt-1")
        )
        subscription_collection = MockMongoCollection()
        subscription_collection.find_one = AsyncMock(return_value=None)

        email_repo = EmailRepository(email_collection)
        template_repo = TemplateRepository(template_collection)
        tracking_repo = TrackingRepository(tracking_collection)
        subscription_repo = SubscriptionRepository(subscription_collection)

        engine = TemplateEngine()
        template_service = TemplateService(template_repo, engine)
        subscription_service = SubscriptionService(subscription_repo)
        tracking_service = TrackingService(tracking_repo, email_repo)

        provider = MockProvider("mock")
        manager = ProviderFailoverManager([(provider, 1)])
        queue = InMemoryEmailQueue()

        service = EmailService(
            email_repo=email_repo,
            template_service=template_service,
            subscription_service=subscription_service,
            provider_manager=manager,
            queue=queue,
            tracking_service=tracking_service,
        )
        return service, queue

    @pytest.mark.asyncio
    async def test_send_email_enqueue(self, sample_email_create):
        service, queue = self._build_service()
        response = await service.send_email(sample_email_create, enqueue=True)
        assert response.status == EmailStatus.QUEUED

        # 验证邮件已入队
        email_id = await queue.dequeue(timeout=1)
        assert email_id is not None
