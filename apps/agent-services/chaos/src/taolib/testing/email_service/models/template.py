"""Email template models."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .enums import EmailType


class TemplateBase(BaseModel):
    """Shared template fields."""

    name: str = Field(description="Template unique name")
    description: str = Field(default="", description="Template description")
    subject_template: str = Field(description="Subject line with variable placeholders")
    html_template: str = Field(description="HTML body with Jinja2 syntax")
    text_template: str | None = Field(
        default=None, description="Plain text fallback template"
    )
    email_type: EmailType = Field(
        default=EmailType.TRANSACTIONAL, description="Email type"
    )
    variables_schema: dict[str, str] = Field(
        default_factory=dict,
        description="Variable name to type mapping for documentation",
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")


class TemplateCreate(TemplateBase):
    """Template creation request."""

    pass


class TemplateUpdate(BaseModel):
    """Template update request (all fields optional)."""

    name: str | None = None
    description: str | None = None
    subject_template: str | None = None
    html_template: str | None = None
    text_template: str | None = None
    email_type: EmailType | None = None
    variables_schema: dict[str, str] | None = None
    tags: list[str] | None = None
    is_active: bool | None = None


class TemplateResponse(TemplateBase):
    """Template API response."""

    id: str = Field(alias="_id")
    is_active: bool = Field(default=True)
    version: int = Field(default=1)
    created_at: datetime = Field(description="Creation time")
    updated_at: datetime = Field(description="Last update time")

    model_config = {"from_attributes": True, "populate_by_name": True}


class TemplateDocument(TemplateBase):
    """Template MongoDB document."""

    id: str = Field(alias="_id")
    is_active: bool = Field(default=True)
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str = Field(default="system")

    model_config = {"populate_by_name": True}

    def to_response(self) -> TemplateResponse:
        """Convert to API response model."""
        return TemplateResponse(
            _id=self.id,
            name=self.name,
            description=self.description,
            subject_template=self.subject_template,
            html_template=self.html_template,
            text_template=self.text_template,
            email_type=self.email_type,
            variables_schema=self.variables_schema,
            tags=self.tags,
            is_active=self.is_active,
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
