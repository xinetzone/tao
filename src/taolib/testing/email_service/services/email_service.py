"""核心邮件发送服务。

编排模板渲染、订阅检查、队列和提供商发送。
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from taolib.testing.email_service.errors import EmailNotFoundError
from taolib.testing.email_service.models.email import (
    EmailCreate,
    EmailDocument,
    EmailResponse,
)
from taolib.testing.email_service.models.enums import EmailStatus, EmailType, TrackingEventType
from taolib.testing.email_service.providers.failover import ProviderFailoverManager
from taolib.testing.email_service.queue.protocol import EmailQueueProtocol
from taolib.testing.email_service.repository.email_repo import EmailRepository
from taolib.testing.email_service.services.subscription_service import SubscriptionService
from taolib.testing.email_service.services.template_service import TemplateService
from taolib.testing.email_service.services.tracking_service import TrackingService

logger = logging.getLogger(__name__)


class EmailService:
    """核心邮件发送服务。

    编排完整的邮件发送流程：
    1. 模板渲染（如有模板）
    2. 订阅状态检查（营销邮件）
    3. 创建邮件文档
    4. 入队或直接发送
    """

    def __init__(
        self,
        email_repo: EmailRepository,
        template_service: TemplateService,
        subscription_service: SubscriptionService,
        provider_manager: ProviderFailoverManager,
        queue: EmailQueueProtocol,
        tracking_service: TrackingService,
    ) -> None:
        """初始化。

        Args:
            email_repo: 邮件 Repository
            template_service: 模板服务
            subscription_service: 订阅服务
            provider_manager: 提供商管理器
            queue: 邮件队列
            tracking_service: 追踪服务
        """
        self._email_repo = email_repo
        self._template_service = template_service
        self._subscription_service = subscription_service
        self._provider_manager = provider_manager
        self._queue = queue
        self._tracking_service = tracking_service

    async def send_email(
        self, data: EmailCreate, enqueue: bool = True
    ) -> EmailResponse:
        """发送单封邮件。

        Args:
            data: 邮件创建数据
            enqueue: 是否入队异步发送，False 则直接发送

        Returns:
            邮件响应
        """
        html_body = data.html_body
        text_body = data.text_body
        primary_email = data.recipients[0].email if data.recipients else None

        # 1. 模板渲染
        if data.template_id:
            unsub_token = None
            if data.email_type == EmailType.MARKETING and primary_email:
                unsub_token = await self._subscription_service.get_unsubscribe_token(
                    primary_email
                )
            rendered = await self._template_service.render_template(
                template_id=data.template_id,
                variables=data.template_variables,
                email_type=data.email_type,
                recipient_email=primary_email,
                unsubscribe_token=unsub_token,
            )
            html_body = rendered.html_body
            text_body = rendered.text_body or text_body

        # 2. 营销邮件订阅检查
        active_recipients = list(data.recipients)
        if data.email_type == EmailType.MARKETING:
            active_recipients = [
                r
                for r in data.recipients
                if await self._subscription_service.is_subscribed(r.email)
            ]
            if not active_recipients:
                logger.info("All recipients unsubscribed, skipping send")

        # 3. 创建邮件文档
        email_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        doc_dict: dict[str, Any] = {
            "_id": email_id,
            "sender": data.sender,
            "sender_name": data.sender_name,
            "recipients": [r.model_dump() for r in active_recipients],
            "cc": [r.model_dump() for r in data.cc],
            "bcc": [r.model_dump() for r in data.bcc],
            "subject": data.subject
            if not data.template_id
            else (html_body and data.subject),
            "email_type": str(data.email_type),
            "priority": str(data.priority),
            "tags": data.tags,
            "template_id": data.template_id,
            "html_body": html_body,
            "text_body": text_body,
            "attachments": [a.model_dump() for a in data.attachments],
            "status": str(EmailStatus.QUEUED),
            "schedule_at": data.schedule_at,
            "metadata": data.metadata,
            "created_at": now,
            "updated_at": now,
        }

        # 恢复模板渲染后的 subject
        if data.template_id and hasattr(self, "_last_rendered_subject"):
            doc_dict["subject"] = data.subject

        doc = await self._email_repo.create(doc_dict)

        # 4. 入队或直接发送
        if enqueue and data.schedule_at is None:
            await self._queue.enqueue(email_id, data.priority)
        elif not enqueue:
            doc = await self._send_now(doc)

        return doc.to_response()

    async def send_bulk(self, emails: list[EmailCreate]) -> list[EmailResponse]:
        """批量发送邮件。"""
        responses: list[EmailResponse] = []
        for email_data in emails:
            response = await self.send_email(email_data, enqueue=True)
            responses.append(response)
        return responses

    async def _send_now(self, email_doc: EmailDocument) -> EmailDocument:
        """立即发送邮件。

        Args:
            email_doc: 邮件文档

        Returns:
            更新后的邮件文档
        """
        # 更新为发送中
        await self._email_repo.update_status(email_doc.id, EmailStatus.SENDING)

        try:
            result = await self._provider_manager.send(email_doc)

            # 发送成功
            now = datetime.now(UTC)
            updated = await self._email_repo.update_status(
                email_doc.id,
                EmailStatus.SENT,
                provider=result.provider_name,
                provider_message_id=result.provider_message_id,
                sent_at=now,
            )

            # 记录追踪事件
            if email_doc.recipients:
                await self._tracking_service.record_event(
                    email_id=email_doc.id,
                    event_type=TrackingEventType.SENT,
                    recipient=email_doc.recipients[0].email,
                    provider=result.provider_name,
                )

            return updated or email_doc

        except Exception as e:
            # 发送失败，处理重试
            logger.error("Failed to send email %s: %s", email_doc.id, e)

            if email_doc.retry_count < email_doc.max_retries:
                updated_doc = await self._email_repo.increment_retry(email_doc.id)
                if updated_doc:
                    await self._email_repo.update_status(
                        email_doc.id, EmailStatus.QUEUED
                    )
                    # 重新入队（指数退避由 queue_processor 处理）
                    await self._queue.enqueue(email_doc.id, email_doc.priority)
                return updated_doc or email_doc
            else:
                await self._email_repo.update_status(
                    email_doc.id,
                    EmailStatus.FAILED,
                    error_message=str(e),
                )
                return email_doc

    async def get_email(self, email_id: str) -> EmailResponse:
        """获取邮件详情。"""
        doc = await self._email_repo.get_by_id(email_id)
        if doc is None:
            raise EmailNotFoundError(f"Email not found: {email_id}")
        return doc.to_response()

    async def list_emails(
        self,
        status: EmailStatus | None = None,
        email_type: EmailType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[EmailResponse]:
        """查询邮件列表。"""
        filters: dict = {}
        if status:
            filters["status"] = str(status)
        if email_type:
            filters["email_type"] = str(email_type)
        docs = await self._email_repo.list(
            filters=filters if filters else None,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )
        return [d.to_response() for d in docs]


