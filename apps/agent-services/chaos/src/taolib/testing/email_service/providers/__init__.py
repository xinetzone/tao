"""邮件提供商层。"""

from .failover import ProviderFailoverManager
from .mailgun import MailgunProvider
from .protocol import EmailProviderProtocol, ProviderHealthStatus, SendResult
from .sendgrid import SendGridProvider
from .ses import SESProvider

try:
    from .smtp import SMTPProvider
except ImportError:
    SMTPProvider = None  # aiosmtplib not installed

__all__ = [
    "EmailProviderProtocol",
    "MailgunProvider",
    "ProviderFailoverManager",
    "ProviderHealthStatus",
    "SESProvider",
    "SendGridProvider",
    "SendResult",
]
if SMTPProvider is not None:
    __all__.append("SMTPProvider")


