"""分片上传端点。"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from taolib.testing.file_storage.models.upload import (
    UploadSessionCreate,
    UploadSessionResponse,
)
from taolib.testing.file_storage.services.upload_service import UploadService

router = APIRouter()


@router.post(
    "",
    response_model=UploadSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="初始化分片上传",
)
async def init_upload(
    data: UploadSessionCreate,
    upload_service: UploadService = Depends(),
):
    """初始化分片上传会话。"""
    return await upload_service.init_upload(data)


@router.get(
    "/{session_id}", response_model=UploadSessionResponse, summary="获取上传状态"
)
async def get_upload_status(
    session_id: str,
    upload_service: UploadService = Depends(),
):
    """获取上传状态和进度。"""
    status_resp = await upload_service.get_upload_status(session_id)
    if status_resp is None:
        raise HTTPException(status_code=404, detail="上传会话不存在")
    return status_resp


@router.put(
    "/{session_id}/chunks/{chunk_index}",
    summary="上传分片",
)
async def upload_chunk(
    session_id: str,
    chunk_index: int,
    file: UploadFile,
    checksum: str | None = Query(None),
    upload_service: UploadService = Depends(),
):
    """上传分片数据。"""
    content = await file.read()
    try:
        chunk = await upload_service.upload_chunk(
            session_id, chunk_index, content, checksum
        )
        return chunk.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{session_id}/complete",
    summary="完成上传",
)
async def complete_upload(
    session_id: str,
    upload_service: UploadService = Depends(),
):
    """完成分片上传并创建文件记录。"""
    try:
        result = await upload_service.complete_upload(session_id)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{session_id}/abort",
    summary="中止上传",
)
async def abort_upload(
    session_id: str,
    upload_service: UploadService = Depends(),
):
    """中止分片上传。"""
    try:
        success = await upload_service.abort_upload(session_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


