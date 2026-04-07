"""Email service enumerations."""

from enum import StrEnum


class EmailStatus(StrEnum):
    """Email delivery status."""

    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"
    REJECTED = "rejected"


class EmailType(StrEnum):
    """Email category type."""

    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"


class EmailPriority(StrEnum):
    """Email sending priority."""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ProviderType(StrEnum):
    """Email service provider type."""

    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    SES = "ses"
    SMTP = "smtp"


class TrackingEventType(StrEnum):
    """Tracking event type for email analytics."""

    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    COMPLAINED = "complained"
    UNSUBSCRIBED = "unsubscribed"


class BounceType(StrEnum):
    """Bounce classification."""

    HARD = "hard"
    SOFT = "soft"
    UNDETERMINED = "undetermined"


class SubscriptionStatus(StrEnum):
    """Subscription status."""

    ACTIVE = "active"
    UNSUBSCRIBED = "unsubscribed"
