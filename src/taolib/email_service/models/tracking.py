"""Email tracking event models."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .enums import BounceType, TrackingEventType


class TrackingEventBase(BaseModel):
    """Shared tracking event fields."""

    email_id: str = Field(description="Associated email ID")
    event_type: TrackingEventType = Field(description="Event type")
    recipient: str = Field(description="Recipient email address")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Event timestamp"
    )


class TrackingEventDocument(TrackingEventBase):
    """Tracking event MongoDB document."""

    id: str = Field(alias="_id")
    provider: str | None = Field(default=None, description="Provider that reported")
    ip_address: str | None = Field(default=None, description="Client IP (opens/clicks)")
    user_agent: str | None = Field(
        default=None, description="Client user agent (opens/clicks)"
    )
    click_url: str | None = Field(default=None, description="Clicked URL (clicks only)")
    bounce_type: BounceType | None = Field(
        default=None, description="Bounce type (bounces only)"
    )
    bounce_reason: str | None = Field(
        default=None, description="Bounce reason (bounces only)"
    )
    raw_payload: dict | None = Field(
        default=None, description="Raw webhook payload from provider"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}

    def to_response(self) -> TrackingEventResponse:
        """Convert to API response model."""
        return TrackingEventResponse(
            _id=self.id,
            email_id=self.email_id,
            event_type=self.event_type,
            recipient=self.recipient,
            timestamp=self.timestamp,
            provider=self.provider,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            click_url=self.click_url,
            bounce_type=self.bounce_type,
            bounce_reason=self.bounce_reason,
            created_at=self.created_at,
        )


class TrackingEventResponse(TrackingEventBase):
    """Tracking event API response."""

    id: str = Field(alias="_id")
    provider: str | None = Field(default=None)
    ip_address: str | None = Field(default=None)
    user_agent: str | None = Field(default=None)
    click_url: str | None = Field(default=None)
    bounce_type: BounceType | None = Field(default=None)
    bounce_reason: str | None = Field(default=None)
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
