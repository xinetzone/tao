
from pydantic import BaseModel, Field


class QRGenerateRequest(BaseModel):
    content: str = Field(..., min_length=1, description="QR code content")
    fg_color: str = "#7c3aed"
    bg_color: str = "#0f1117"
    size: int = Field(512, ge=128, le=2048)
    error_correction: str = "H"
    module_style: str = "square"
    logo_base64: str | None = None
    logo_size: int = Field(20, ge=10, le=30)


class QRBatchRequest(BaseModel):
    items: list[dict[str, str]] = Field(..., min_items=1)
    fg_color: str = "#7c3aed"
    bg_color: str = "#0f1117"
    size: int = Field(512, ge=128, le=2048)
    error_correction: str = "H"
    module_style: str = "square"


class QRGenerateResponse(BaseModel):
    success: bool
    data_url: str | None = None
    svg: str | None = None
    size: int
    error: str | None = None


class QRBatchResponse(BaseModel):
    success: bool
    count: int
    error: str | None = None


