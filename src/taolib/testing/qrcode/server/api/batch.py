import io
import zipfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from taolib.testing.qrcode.generator import create_qr_image
from taolib.testing.qrcode.models import QRBatchRequest, QRBatchResponse

router = APIRouter()


@router.post("", response_model=QRBatchResponse)
async def batch_generate_qr(request: QRBatchRequest) -> StreamingResponse:
    if not request.items:
        raise HTTPException(status_code=400, detail="Items list is required")

    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, item in enumerate(request.items):
                content = item.get("content", "")
                label = item.get("label", f"qr_{i + 1}")
                if not content:
                    continue

                img = create_qr_image(
                    content,
                    fg_color=request.fg_color,
                    bg_color=request.bg_color,
                    size=request.size,
                    error_correction=request.error_correction,
                    module_style=request.module_style,
                )
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG", quality=95)
                img_buffer.seek(0)

                safe_label = "".join(
                    c if c.isalnum() or c in "-_" else "_" for c in label
                )
                zf.writestr(f"{safe_label}.png", img_buffer.getvalue())

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=qr-batch.zip"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


