"""邮件服务系统。

提供完整的事务性邮件和营销邮件发送、模板管理、投递追踪和退订管理功能。
支持多个邮件服务提供商（SendGrid、Mailgun、Amazon SES、SMTP）自动故障转移。
"""

from taolib.email_service.errors import (
    AllProvidersFailedError,
    EmailNotFoundError,
    EmailServiceError,
    ProviderError,
    QueueError,
    SubscriptionError,
    TemplateNotFoundError,
    TemplateRenderError,
)
from taolib.email_service.models import (
    BounceType,
    EmailAttachment,
    EmailCreate,
    EmailDocument,
    EmailPriority,
    EmailRecipient,
    EmailResponse,
    EmailStatus,
    EmailType,
    ProviderType,
    SubscriptionDocument,
    SubscriptionResponse,
    SubscriptionStatus,
    TemplateCreate,
    TemplateDocument,
    TemplateResponse,
    TemplateUpdate,
    TrackingEventDocument,
    TrackingEventResponse,
    TrackingEventType,
)
from taolib.email_service.providers import (
    EmailProviderProtocol,
    MailgunProvider,
    ProviderFailoverManager,
    ProviderHealthStatus,
    SendGridProvider,
    SendResult,
    SESProvider,
)

try:
    from taolib.email_service.providers import SMTPProvider
except ImportError:
    SMTPProvider = None  # aiosmtplib not installed
from taolib.email_service.queue import (
    EmailQueueProtocol,
    InMemoryEmailQueue,
    RedisEmailQueue,
)
from taolib.email_service.services import (
    BounceHandler,
    EmailAnalytics,
    EmailService,
    QueueProcessor,
    SubscriptionService,
    TemplateService,
    TrackingService,
)
from taolib.email_service.template import RenderedEmail, TemplateEngine

__all__ = [
    # Errors
    "AllProvidersFailedError",
    "EmailNotFoundError",
    "EmailServiceError",
    "ProviderError",
    "QueueError",
    "SubscriptionError",
    "TemplateNotFoundError",
    "TemplateRenderError",
    # Enums
    "BounceType",
    "EmailPriority",
    "EmailStatus",
    "EmailType",
    "ProviderType",
    "SubscriptionStatus",
    "TrackingEventType",
    # Models
    "EmailAttachment",
    "EmailCreate",
    "EmailDocument",
    "EmailRecipient",
    "EmailResponse",
    "SubscriptionDocument",
    "SubscriptionResponse",
    "TemplateCreate",
    "TemplateDocument",
    "TemplateResponse",
    "TemplateUpdate",
    "TrackingEventDocument",
    "TrackingEventResponse",
    # Providers
    "EmailProviderProtocol",
    "MailgunProvider",
    "ProviderFailoverManager",
    "ProviderHealthStatus",
    "SESProvider",
    "SendGridProvider",
    "SendResult",
    # Queue
    "EmailQueueProtocol",
    "InMemoryEmailQueue",
    "RedisEmailQueue",
    # Template
    "RenderedEmail",
    "TemplateEngine",
    # Services
    "BounceHandler",
    "EmailAnalytics",
    "EmailService",
    "QueueProcessor",
    "SubscriptionService",
    "TemplateService",
    "TrackingService",
]
if SMTPProvider is not None:
    __all__.append("SMTPProvider")
