"""模型测试。"""

from taolib.testing.email_service.models.email import (
    EmailDocument,
    EmailRecipient,
    EmailResponse,
)
from taolib.testing.email_service.models.enums import (
    BounceType,
    EmailPriority,
    EmailStatus,
    EmailType,
    ProviderType,
    SubscriptionStatus,
    TrackingEventType,
)
from taolib.testing.email_service.models.subscription import SubscriptionDocument
from taolib.testing.email_service.models.template import (
    TemplateUpdate,
)
from taolib.testing.email_service.models.tracking import TrackingEventDocument


class TestEnums:
    def test_email_status_values(self):
        assert EmailStatus.QUEUED == "queued"
        assert EmailStatus.SENT == "sent"
        assert EmailStatus.DELIVERED == "delivered"
        assert EmailStatus.BOUNCED == "bounced"
        assert EmailStatus.FAILED == "failed"

    def test_email_type_values(self):
        assert EmailType.TRANSACTIONAL == "transactional"
        assert EmailType.MARKETING == "marketing"

    def test_priority_values(self):
        assert EmailPriority.HIGH == "high"
        assert EmailPriority.NORMAL == "normal"
        assert EmailPriority.LOW == "low"

    def test_provider_type_values(self):
        assert ProviderType.SENDGRID == "sendgrid"
        assert ProviderType.MAILGUN == "mailgun"
        assert ProviderType.SES == "ses"
        assert ProviderType.SMTP == "smtp"

    def test_bounce_type_values(self):
        assert BounceType.HARD == "hard"
        assert BounceType.SOFT == "soft"

    def test_tracking_event_type_values(self):
        assert TrackingEventType.SENT == "sent"
        assert TrackingEventType.OPENED == "opened"
        assert TrackingEventType.CLICKED == "clicked"

    def test_subscription_status_values(self):
        assert SubscriptionStatus.ACTIVE == "active"
        assert SubscriptionStatus.UNSUBSCRIBED == "unsubscribed"


class TestEmailModels:
    def test_email_create(self, sample_email_create):
        assert sample_email_create.sender == "test@example.com"
        assert len(sample_email_create.recipients) == 1
        assert sample_email_create.email_type == EmailType.TRANSACTIONAL

    def test_email_document_defaults(self):
        doc = EmailDocument(
            _id="test-1",
            sender="a@b.com",
            recipients=[EmailRecipient(email="c@d.com")],
            subject="Test",
        )
        assert doc.status == EmailStatus.QUEUED
        assert doc.retry_count == 0
        assert doc.max_retries == 3
        assert doc.created_at is not None

    def test_email_document_to_response(self, sample_email_document):
        response = sample_email_document.to_response()
        assert isinstance(response, EmailResponse)
        assert response.id == "email-001"
        assert response.status == EmailStatus.QUEUED
        assert response.sender == "test@example.com"


class TestTemplateModels:
    def test_template_create(self, sample_template_create):
        assert sample_template_create.name == "welcome"
        assert "{{ name }}" in sample_template_create.subject_template

    def test_template_update_partial(self):
        update = TemplateUpdate(description="Updated description")
        dumped = update.model_dump(exclude_none=True)
        assert "description" in dumped
        assert "name" not in dumped

    def test_template_document_to_response(self, sample_template_document):
        response = sample_template_document.to_response()
        assert response.id == "tmpl-001"
        assert response.name == "welcome"
        assert response.version == 1


class TestTrackingModels:
    def test_tracking_event_document(self):
        doc = TrackingEventDocument(
            _id="evt-001",
            email_id="email-001",
            event_type=TrackingEventType.DELIVERED,
            recipient="user@example.com",
        )
        response = doc.to_response()
        assert response.id == "evt-001"
        assert response.event_type == TrackingEventType.DELIVERED


class TestSubscriptionModels:
    def test_subscription_document(self):
        doc = SubscriptionDocument(
            _id="sub-001",
            email="user@example.com",
            status=SubscriptionStatus.ACTIVE,
            unsubscribe_token="token-123",
        )
        response = doc.to_response()
        assert response.email == "user@example.com"
        assert response.status == SubscriptionStatus.ACTIVE



