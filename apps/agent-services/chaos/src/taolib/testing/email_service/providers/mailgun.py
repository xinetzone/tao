"""Mailgun 邮件提供商实现。"""

import logging
import time

import httpx

from taolib.testing.email_service.models.email import EmailDocument

from .protocol import ProviderHealthStatus, SendResult

logger = logging.getLogger(__name__)


class MailgunProvider:
    """Mailgun 邮件提供商。

    通过 Mailgun HTTP API 发送邮件。
    """

    def __init__(self, api_key: str, domain: str) -> None:
        """初始化。

        Args:
            api_key: Mailgun API Key
            domain: Mailgun 发送域名
        """
        self._api_key = api_key
        self._domain = domain
        self._client = httpx.AsyncClient(
            base_url=f"https://api.mailgun.net/v3/{domain}",
            auth=("api", api_key),
            timeout=30.0,
        )

    @property
    def name(self) -> str:
        """提供商名称。"""
        return "mailgun"

    async def send(self, email: EmailDocument) -> SendResult:
        """通过 Mailgun API 发送邮件。"""
        start = time.monotonic()
        try:
            data = self._build_form_data(email)
            response = await self._client.post("/messages", data=data)
            latency = (time.monotonic() - start) * 1000

            if response.status_code == 200:
                body = response.json()
                return SendResult(
                    success=True,
                    provider_name=self.name,
                    provider_message_id=body.get("id", ""),
                    latency_ms=latency,
                )
            return SendResult(
                success=False,
                provider_name=self.name,
                error_message=f"HTTP {response.status_code}: {response.text}",
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
        """检查 Mailgun 可用性。"""
        try:
            client = httpx.AsyncClient(
                base_url="https://api.mailgun.net/v3",
                auth=("api", self._api_key),
                timeout=10.0,
            )
            response = await client.get(f"/domains/{self._domain}")
            await client.aclose()
            return ProviderHealthStatus(
                provider_name=self.name,
                is_healthy=response.status_code == 200,
            )
        except Exception as e:
            return ProviderHealthStatus(
                provider_name=self.name,
                is_healthy=False,
                last_error=str(e),
            )

    def _build_form_data(self, email: EmailDocument) -> dict:
        """构建 Mailgun 表单数据。"""
        sender = email.sender
        if email.sender_name:
            sender = f"{email.sender_name} <{email.sender}>"

        data: dict = {
            "from": sender,
            "to": [r.email for r in email.recipients],
            "subject": email.subject,
        }

        if email.cc:
            data["cc"] = [r.email for r in email.cc]
        if email.bcc:
            data["bcc"] = [r.email for r in email.bcc]
        if email.html_body:
            data["html"] = email.html_body
        if email.text_body:
            data["text"] = email.text_body
        if email.tags:
            data["o:tag"] = email.tags

        return data


