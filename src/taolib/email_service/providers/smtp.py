"""SMTP 邮件提供商实现。"""

import logging
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from taolib.email_service.models.email import EmailDocument

from .protocol import ProviderHealthStatus, SendResult

logger = logging.getLogger(__name__)


class SMTPProvider:
    """SMTP 邮件提供商。

    通过标准 SMTP 协议发送邮件。
    """

    def __init__(
        self,
        host: str,
        port: int = 587,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
    ) -> None:
        """初始化。

        Args:
            host: SMTP 服务器地址
            port: SMTP 端口
            username: 认证用户名
            password: 认证密码
            use_tls: 是否使用 STARTTLS
        """
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls

    @property
    def name(self) -> str:
        """提供商名称。"""
        return "smtp"

    async def send(self, email: EmailDocument) -> SendResult:
        """通过 SMTP 发送邮件。"""
        import aiosmtplib

        start = time.monotonic()
        try:
            message = self._build_message(email)
            recipients = (
                [r.email for r in email.recipients]
                + [r.email for r in email.cc]
                + [r.email for r in email.bcc]
            )

            await aiosmtplib.send(
                message,
                hostname=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                start_tls=self._use_tls,
                recipients=recipients,
            )
            latency = (time.monotonic() - start) * 1000

            return SendResult(
                success=True,
                provider_name=self.name,
                provider_message_id=message["Message-ID"],
                latency_ms=latency,
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return SendResult(
                success=False,
                provider_name=self.name,
                error_message=str(e),
                latency_ms=latency,
            )

    async def send_bulk(self, emails: list[EmailDocument]) -> list[SendResult]:
        """批量发送（逐封发送）。"""
        return [await self.send(email) for email in emails]

    async def check_health(self) -> ProviderHealthStatus:
        """检查 SMTP 服务器可用性。"""
        import aiosmtplib

        try:
            smtp = aiosmtplib.SMTP(hostname=self._host, port=self._port, timeout=10)
            await smtp.connect()
            if self._use_tls:
                await smtp.starttls()
            await smtp.noop()
            await smtp.quit()
            return ProviderHealthStatus(provider_name=self.name, is_healthy=True)
        except Exception as e:
            return ProviderHealthStatus(
                provider_name=self.name,
                is_healthy=False,
                last_error=str(e),
            )

    def _build_message(self, email: EmailDocument) -> MIMEMultipart:
        """构建 MIME 邮件消息。"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = email.subject
        msg["From"] = (
            f"{email.sender_name} <{email.sender}>"
            if email.sender_name
            else email.sender
        )
        msg["To"] = ", ".join(r.email for r in email.recipients)

        if email.cc:
            msg["Cc"] = ", ".join(r.email for r in email.cc)

        if email.text_body:
            msg.attach(MIMEText(email.text_body, "plain", "utf-8"))
        if email.html_body:
            msg.attach(MIMEText(email.html_body, "html", "utf-8"))

        return msg
