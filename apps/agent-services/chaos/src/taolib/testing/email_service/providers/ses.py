"""Amazon SES 邮件提供商实现。"""

import logging
import time

import httpx

from taolib.testing.email_service.models.email import EmailDocument

from .protocol import ProviderHealthStatus, SendResult

logger = logging.getLogger(__name__)


class SESProvider:
    """Amazon SES 邮件提供商。

    通过 Amazon SES v2 HTTP API 发送邮件。
    需要配置 AWS 凭证和区域。
    """

    def __init__(
        self,
        region: str,
        access_key_id: str,
        secret_access_key: str,
    ) -> None:
        """初始化。

        Args:
            region: AWS 区域 (如 us-east-1)
            access_key_id: AWS Access Key ID
            secret_access_key: AWS Secret Access Key
        """
        self._region = region
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._endpoint = f"https://email.{region}.amazonaws.com"
        self._client = httpx.AsyncClient(timeout=30.0)

    @property
    def name(self) -> str:
        """提供商名称。"""
        return "ses"

    async def send(self, email: EmailDocument) -> SendResult:
        """通过 SES API 发送邮件。

        使用简化的 SES v2 SendEmail API。
        生产环境建议使用 aiobotocore 以获得完整的 AWS 签名支持。
        """
        start = time.monotonic()
        try:
            payload = self._build_payload(email)
            # 简化实现：直接使用 SES v2 SendEmail
            # 生产环境应使用 aiobotocore 处理 AWS Signature V4
            response = await self._client.post(
                f"{self._endpoint}/v2/email/outbound-emails",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Amz-Access-Key": self._access_key_id,
                },
            )
            latency = (time.monotonic() - start) * 1000

            if response.status_code == 200:
                body = response.json()
                return SendResult(
                    success=True,
                    provider_name=self.name,
                    provider_message_id=body.get("MessageId", ""),
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
        """检查 SES 可用性。"""
        try:
            response = await self._client.get(
                f"{self._endpoint}/v2/email/account",
                headers={"X-Amz-Access-Key": self._access_key_id},
            )
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
        """构建 SES v2 请求体。"""
        destination: dict = {
            "ToAddresses": [r.email for r in email.recipients],
        }
        if email.cc:
            destination["CcAddresses"] = [r.email for r in email.cc]
        if email.bcc:
            destination["BccAddresses"] = [r.email for r in email.bcc]

        body: dict = {}
        if email.html_body:
            body["Html"] = {"Data": email.html_body, "Charset": "UTF-8"}
        if email.text_body:
            body["Text"] = {"Data": email.text_body, "Charset": "UTF-8"}

        return {
            "FromEmailAddress": email.sender,
            "Destination": destination,
            "Content": {
                "Simple": {
                    "Subject": {"Data": email.subject, "Charset": "UTF-8"},
                    "Body": body,
                }
            },
        }


