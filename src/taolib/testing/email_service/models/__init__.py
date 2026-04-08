"""Email service data models.

Exports public model classes for email, template, tracking,
and subscription management.
"""

from .email import (
    EmailAttachment,
    EmailCreate,
    EmailDocument,
    EmailRecipient,
    EmailResponse,
)
from .enums import (
    BounceType,
    EmailPriority,
    EmailStatus,
    EmailType,
    ProviderType,
    TrackingEventType,
)
from .subscription import (
    SubscriptionDocument,
    SubscriptionResponse,
    SubscriptionStatus,
)
from .template import (
    TemplateCreate,
    TemplateDocument,
    TemplateResponse,
    TemplateUpdate,
)
from .tracking import TrackingEventDocument, TrackingEventResponse

__all__ = [
    # Enums
    "BounceType",
    "EmailPriority",
    "EmailStatus",
    "EmailType",
    "ProviderType",
    "TrackingEventType",
    # Email models
    "EmailAttachment",
    "EmailCreate",
    "EmailDocument",
    "EmailRecipient",
    "EmailResponse",
    # Template models
    "TemplateCreate",
    "TemplateDocument",
    "TemplateResponse",
    "TemplateUpdate",
    # Tracking models
    "TrackingEventDocument",
    "TrackingEventResponse",
    # Subscription models
    "SubscriptionDocument",
    "SubscriptionResponse",
    "SubscriptionStatus",
]


