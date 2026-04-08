"""签名 URL 端点。"""

from fastapi import APIRouter, Depends, HTTPException

from taolib.testing.file_storage.services.access_service import AccessService

router = APIRouter()


class SignedUrlRequest:
    """签名 URL 请求体。"""

    def __init__(self, file_id: str, expires_in: int = 3600) -> None:
        self.file_id = file_id
        self.expires_in = expires_in


@router.post("", summary="生成签名 URL")
async def generate_signed_url(
    data: SignedUrlRequest,
    access_service: AccessService = Depends(),
):
    """生成签名 URL。"""
    try:
        url = await access_service.generate_signed_url(data.file_id, data.expires_in)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


class ValidateTokenRequest:
    """验证 Token 请求体。"""

    def __init__(self, file_id: str, expires: int, signature: str) -> None:
        self.file_id = file_id
        self.expires = expires
        self.signature = signature


@router.post("/validate", summary="验证签名 Token")
async def validate_token(
    data: ValidateTokenRequest,
    access_service: AccessService = Depends(),
):
    """验证签名 Token。"""
    valid = access_service.validate_token(data.file_id, data.expires, data.signature)
    return {"valid": valid}


