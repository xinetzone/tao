"""事件类型测试。"""

from taolib.email_service.events.types import (
    EmailBouncedEvent,
    EmailClickedEvent,
    EmailDeliveredEvent,
    EmailFailedEvent,
    EmailOpenedEvent,
    EmailQueuedEvent,
    EmailSentEvent,
)


class TestEventTypes:
    def test_email_queued_event(self):
        event = EmailQueuedEvent(
            email_id="e1",
            recipient_count=3,
            priority="normal",
            email_type="transactional",
        )
        d = event.to_dict()
        assert d["event"] == "email.queued"
        assert d["email_id"] == "e1"
        assert d["recipient_count"] == 3

    def test_email_sent_event(self):
        event = EmailSentEvent(
            email_id="e1",
            provider="sendgrid",
            provider_message_id="msg-123",
        )
        d = event.to_dict()
        assert d["event"] == "email.sent"
        assert d["provider"] == "sendgrid"

    def test_email_delivered_event(self):
        event = EmailDeliveredEvent(email_id="e1", recipient="a@b.com")
        d = event.to_dict()
        assert d["event"] == "email.delivered"

    def test_email_opened_event(self):
        event = EmailOpenedEvent(
            email_id="e1",
            recipient="a@b.com",
            ip_address="1.2.3.4",
        )
        d = event.to_dict()
        assert d["ip_address"] == "1.2.3.4"

    def test_email_clicked_event(self):
        event = EmailClickedEvent(
            email_id="e1",
            recipient="a@b.com",
            url="https://example.com",
        )
        d = event.to_dict()
        assert d["url"] == "https://example.com"

    def test_email_bounced_event(self):
        event = EmailBouncedEvent(
            email_id="e1",
            recipient="a@b.com",
            bounce_type="hard",
            reason="Mailbox not found",
        )
        d = event.to_dict()
        assert d["bounce_type"] == "hard"

    def test_email_failed_event(self):
        event = EmailFailedEvent(
            email_id="e1",
            error_message="Timeout",
            retry_count=2,
        )
        d = event.to_dict()
        assert d["retry_count"] == 2

    def test_events_are_frozen(self):
        event = EmailQueuedEvent(
            email_id="e1",
            recipient_count=1,
            priority="high",
            email_type="marketing",
        )
        try:
            event.email_id = "e2"
            assert False, "Should be frozen"
        except AttributeError:
            pass  # Expected for frozen dataclass
