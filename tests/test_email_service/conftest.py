"""邮件服务测试 fixtures。"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.email_service.models.email import EmailCreate, EmailDocument, EmailRecipient
from taolib.email_service.models.enums import EmailPriority, EmailStatus, EmailType
from taolib.email_service.models.template import TemplateCreate, TemplateDocument
from taolib.email_service.providers.protocol import ProviderHealthStatus, SendResult


class MockMongoCollection:
    """Mock MongoDB 集合。"""

    def __init__(self, name: str = "test") -> None:
        self.name = name
        self._data: dict = {}
        self.insert_one = AsyncMock()
        self.find_one = AsyncMock(return_value=None)
        self.find_one_and_update = AsyncMock(return_value=None)
        self.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
        self.count_documents = AsyncMock(return_value=0)
        self.create_index = AsyncMock()
        self.aggregate = MagicMock()

        # find 返回链式调用
        mock_cursor = MagicMock()
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[])
        self.find = MagicMock(return_value=mock_cursor)


class MockProvider:
    """Mock 邮件提供商。"""

    def __init__(self, name: str = "mock", should_fail: bool = False):
        self._name = name
        self._should_fail = should_fail

    @property
    def name(self) -> str:
        return self._name

    async def send(self, email: EmailDocument) -> SendResult:
        if self._should_fail:
            raise Exception(f"{self._name} failed")
        return SendResult(
            success=True,
            provider_name=self._name,
            provider_message_id=f"msg-{self._name}-123",
            latency_ms=50.0,
        )

    async def send_bulk(self, emails: list[EmailDocument]) -> list[SendResult]:
        return [await self.send(e) for e in emails]

    async def check_health(self) -> ProviderHealthStatus:
        return ProviderHealthStatus(
            provider_name=self._name,
            is_healthy=not self._should_fail,
        )


@pytest.fixture
def mock_collection():
    return MockMongoCollection()


@pytest.fixture
def mock_provider():
    return MockProvider("mock_primary")


@pytest.fixture
def failing_provider():
    return MockProvider("mock_failing", should_fail=True)


@pytest.fixture
def sample_email_create() -> EmailCreate:
    return EmailCreate(
        sender="test@example.com",
        sender_name="Test Sender",
        recipients=[
            EmailRecipient(email="user@example.com", name="Test User"),
        ],
        subject="Test Subject",
        html_body="<h1>Hello {{ name }}</h1>",
        text_body="Hello {{ name }}",
        email_type=EmailType.TRANSACTIONAL,
        priority=EmailPriority.NORMAL,
        tags=["test"],
    )


@pytest.fixture
def sample_email_document() -> EmailDocument:
    return EmailDocument(
        _id="email-001",
        sender="test@example.com",
        sender_name="Test",
        recipients=[EmailRecipient(email="user@example.com", name="User")],
        subject="Test",
        email_type=EmailType.TRANSACTIONAL,
        priority=EmailPriority.NORMAL,
        status=EmailStatus.QUEUED,
        html_body="<p>Hello</p>",
        text_body="Hello",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_template_create() -> TemplateCreate:
    return TemplateCreate(
        name="welcome",
        description="Welcome email template",
        subject_template="Welcome, {{ name }}!",
        html_template="<h1>Welcome, {{ name }}!</h1><p>Thanks for joining.</p>",
        text_template="Welcome, {{ name }}! Thanks for joining.",
        email_type=EmailType.TRANSACTIONAL,
        variables_schema={"name": "string"},
        tags=["welcome"],
    )


@pytest.fixture
def sample_template_document() -> TemplateDocument:
    return TemplateDocument(
        _id="tmpl-001",
        name="welcome",
        description="Welcome email",
        subject_template="Welcome, {{ name }}!",
        html_template="<h1>Welcome, {{ name }}!</h1>",
        text_template="Welcome, {{ name }}!",
        email_type=EmailType.TRANSACTIONAL,
        is_active=True,
        version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
