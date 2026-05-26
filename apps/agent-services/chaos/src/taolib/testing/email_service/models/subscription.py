"""Subscription and unsubscribe management models."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .enums import SubscriptionStatus


class SubscriptionDocument(BaseModel):
    """Subscription MongoDB document.

    Tracks whether a recipient has unsubscribed from marketing emails.
    """

    id: str = Field(alias="_id")
    email: str = Field(description="Subscriber email address")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    unsubscribe_reason: str | None = Field(
        default=None, description="Reason for unsubscribing"
    )
    unsubscribe_token: str = Field(description="Unique token for unsubscribe link")
    tags: list[str] = Field(
        default_factory=list,
        description="Subscribed tags/categories",
    )
    subscribed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    unsubscribed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True}

    def to_response(self) -> SubscriptionResponse:
        """Convert to API response model."""
        return SubscriptionResponse(
            _id=self.id,
            email=self.email,
            status=self.status,
            unsubscribe_reason=self.unsubscribe_reason,
            tags=self.tags,
            subscribed_at=self.subscribed_at,
            unsubscribed_at=self.unsubscribed_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class SubscriptionResponse(BaseModel):
    """Subscription API response."""

    id: str = Field(alias="_id")
    email: str
    status: SubscriptionStatus
    unsubscribe_reason: str | None = None
    tags: list[str] = Field(default_factory=list)
    subscribed_at: datetime
    unsubscribed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


