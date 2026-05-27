"""Email message models."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .enums import EmailPriority, EmailStatus, EmailType


class EmailRecipient(BaseModel):
    """Email recipient with optional display name."""

    email: str = Field(description="Recipient email address")
    name: str | None = Field(default=None, description="Display name")


class EmailAttachment(BaseModel):
    """Email attachment metadata."""

    filename: str = Field(description="Attachment filename")
    content_type: str = Field(
        default="application/octet-stream", description="MIME type"
    )
    content_base64: str = Field(description="Base64-encoded file content")


class EmailBase(BaseModel):
    """Shared email fields."""

    sender: str = Field(description="Sender email address (From)")
    sender_name: str | None = Field(default=None, description="Sender display name")
    recipients: list[EmailRecipient] = Field(description="To recipients")
    cc: list[EmailRecipient] = Field(default_factory=list, description="CC recipients")
    bcc: list[EmailRecipient] = Field(
        default_factory=list, description="BCC recipients"
    )
    subject: str = Field(description="Email subject line")
    email_type: EmailType = Field(
        default=EmailType.TRANSACTIONAL, description="Email type"
    )
    priority: EmailPriority = Field(
        default=EmailPriority.NORMAL, description="Sending priority"
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")


class EmailCreate(EmailBase):
    """Email creation request."""

    template_id: str | None = Field(
        default=None, description="Template ID for rendering"
    )
    template_variables: dict[str, str | int | float | bool | list | dict] = Field(
        default_factory=dict, description="Variables for template rendering"
    )
    html_body: str | None = Field(
        default=None, description="HTML body (if no template)"
    )
    text_body: str | None = Field(
        default=None, description="Plain text body (fallback)"
    )
    attachments: list[EmailAttachment] = Field(
        default_factory=list, description="File attachments"
    )
    schedule_at: datetime | None = Field(
        default=None, description="Scheduled send time (UTC)"
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Custom metadata key-value pairs"
    )


class EmailResponse(EmailBase):
    """Email API response."""

    id: str = Field(alias="_id")
    status: EmailStatus = Field(description="Current delivery status")
    provider: str | None = Field(default=None, description="Provider used for sending")
    provider_message_id: str | None = Field(
        default=None, description="Message ID from provider"
    )
    template_id: str | None = Field(default=None)
    html_body: str | None = Field(default=None)
    text_body: str | None = Field(default=None)
    retry_count: int = Field(default=0)
    error_message: str | None = Field(default=None)
    sent_at: datetime | None = Field(default=None)
    delivered_at: datetime | None = Field(default=None)
    opened_at: datetime | None = Field(default=None)
    created_at: datetime = Field(description="Record creation time")
    updated_at: datetime = Field(description="Last update time")
    metadata: dict[str, str] = Field(default_factory=dict)

    model_config = {"from_attributes": True, "populate_by_name": True}


class EmailDocument(EmailBase):
    """Email MongoDB document."""

    id: str = Field(alias="_id")
    status: EmailStatus = Field(default=EmailStatus.QUEUED)
    provider: str | None = Field(default=None)
    provider_message_id: str | None = Field(default=None)
    template_id: str | None = Field(default=None)
    html_body: str | None = Field(default=None)
    text_body: str | None = Field(default=None)
    attachments: list[EmailAttachment] = Field(default_factory=list)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    error_message: str | None = Field(default=None)
    schedule_at: datetime | None = Field(default=None)
    sent_at: datetime | None = Field(default=None)
    delivered_at: datetime | None = Field(default=None)
    opened_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str = Field(default="system")
    metadata: dict[str, str] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    def to_response(self) -> EmailResponse:
        """Convert to API response model."""
        return EmailResponse(
            _id=self.id,
            sender=self.sender,
            sender_name=self.sender_name,
            recipients=self.recipients,
            cc=self.cc,
            bcc=self.bcc,
            subject=self.subject,
            email_type=self.email_type,
            priority=self.priority,
            tags=self.tags,
            status=self.status,
            provider=self.provider,
            provider_message_id=self.provider_message_id,
            template_id=self.template_id,
            html_body=self.html_body,
            text_body=self.text_body,
            retry_count=self.retry_count,
            error_message=self.error_message,
            sent_at=self.sent_at,
            delivered_at=self.delivered_at,
            opened_at=self.opened_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata=self.metadata,
        )
