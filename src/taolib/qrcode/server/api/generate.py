import base64
import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from taolib.qrcode.generator import create_qr_image, create_qr_svg
from taolib.qrcode.models import QRGenerateRequest, QRGenerateResponse

router = APIRouter()


@router.post("", response_model=QRGenerateResponse)
async def generate_qr(request: QRGenerateRequest) -> QRGenerateResponse:
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")

    logo_data = None
    if request.logo_base64:
        try:
            logo_data = base64.b64decode(request.logo_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid logo base64: {e}")

    try:
        img = create_qr_image(
            request.content,
            fg_color=request.fg_color,
            bg_color=request.bg_color,
            size=request.size,
            error_correction=request.error_correction,
            module_style=request.module_style,
            logo_data=logo_data,
            logo_size_pct=request.logo_size,
        )

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", quality=95)
        buffer.seek(0)

        b64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return QRGenerateResponse(
            success=True,
            data_url=f"data:image/png;base64,{b64_img}",
            size=request.size,
        )
    except Exception as e:
        return QRGenerateResponse(success=False, size=request.size, error=str(e))


@router.post("/svg", response_model=QRGenerateResponse)
async def generate_qr_svg_endpoint(request: QRGenerateRequest) -> QRGenerateResponse:
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")

    try:
        svg_str = create_qr_svg(
            request.content,
            fg_color=request.fg_color,
            bg_color=request.bg_color,
            size=request.size,
            error_correction=request.error_correction,
        )
        return QRGenerateResponse(success=True, svg=svg_str, size=request.size)
    except Exception as e:
        return QRGenerateResponse(success=False, size=request.size, error=str(e))


@router.post("/download")
async def download_qr(request: QRGenerateRequest) -> StreamingResponse:
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")

    logo_data = None
    if request.logo_base64:
        try:
            logo_data = base64.b64decode(request.logo_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid logo base64: {e}")

    try:
        img = create_qr_image(
            request.content,
            fg_color=request.fg_color,
            bg_color=request.bg_color,
            size=request.size,
            error_correction=request.error_correction,
            module_style=request.module_style,
            logo_data=logo_data,
            logo_size_pct=request.logo_size,
        )
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", quality=95)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=qrcode-{request.size}x{request.size}.png"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
