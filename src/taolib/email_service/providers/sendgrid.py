"""SendGrid 邮件提供商实现。"""

import logging
import time

import httpx

from taolib.email_service.models.email import EmailDocument

from .protocol import ProviderHealthStatus, SendResult

logger = logging.getLogger(__name__)


class SendGridProvider:
    """SendGrid 邮件提供商。

    通过 SendGrid v3 Mail Send API 发送邮件。
    """

    def __init__(
        self,
        api_key: str,
        sender_email: str | None = None,
        sender_name: str | None = None,
    ) -> None:
        """初始化。

        Args:
            api_key: SendGrid API Key
            sender_email: 默认发送者邮箱
            sender_name: 默认发送者名称
        """
        self._api_key = api_key
        self._sender_email = sender_email
        self._sender_name = sender_name
        self._client = httpx.AsyncClient(
            base_url="https://api.sendgrid.com",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    @property
    def name(self) -> str:
        """提供商名称。"""
        return "sendgrid"

    async def send(self, email: EmailDocument) -> SendResult:
        """通过 SendGrid API 发送邮件。"""
        start = time.monotonic()
        try:
            payload = self._build_payload(email)
            response = await self._client.post("/v3/mail/send", json=payload)
            latency = (time.monotonic() - start) * 1000

            if response.status_code in (200, 201, 202):
                message_id = response.headers.get("X-Message-Id", "")
                return SendResult(
                    success=True,
                    provider_name=self.name,
                    provider_message_id=message_id,
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
        """检查 SendGrid 可用性。"""
        try:
            response = await self._client.get("/v3/scopes")
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

    def _build_payload(self, email: EmailDocument) -> dict:
        """构建 SendGrid v3 API 请求体。"""
        sender = email.sender or self._sender_email or ""
        sender_name = email.sender_name or self._sender_name

        personalizations = [
            {
                "to": [
                    {"email": r.email, **({"name": r.name} if r.name else {})}
                    for r in email.recipients
                ],
            }
        ]
        if email.cc:
            personalizations[0]["cc"] = [
                {"email": r.email, **({"name": r.name} if r.name else {})}
                for r in email.cc
            ]
        if email.bcc:
            personalizations[0]["bcc"] = [
                {"email": r.email, **({"name": r.name} if r.name else {})}
                for r in email.bcc
            ]

        content = []
        if email.text_body:
            content.append({"type": "text/plain", "value": email.text_body})
        if email.html_body:
            content.append({"type": "text/html", "value": email.html_body})

        payload: dict = {
            "personalizations": personalizations,
            "from": {"email": sender, **({"name": sender_name} if sender_name else {})},
            "subject": email.subject,
            "content": content or [{"type": "text/plain", "value": ""}],
        }

        if email.tags:
            payload["categories"] = email.tags[:10]  # SendGrid 最多 10 个

        return payload
