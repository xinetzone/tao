"""存储桶端点。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from taolib.file_storage.models.bucket import BucketCreate, BucketResponse, BucketUpdate
from taolib.file_storage.services.bucket_service import BucketService

router = APIRouter()


@router.get("", response_model=list[BucketResponse], summary="列出所有桶")
async def list_buckets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    bucket_service: BucketService = Depends(),
):
    """列出所有存储桶。"""
    return await bucket_service.list_buckets(skip=skip, limit=limit)


@router.post(
    "",
    response_model=BucketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建桶",
)
async def create_bucket(
    data: BucketCreate,
    bucket_service: BucketService = Depends(),
):
    """创建存储桶。"""
    return await bucket_service.create_bucket(data)


@router.get("/{bucket_id}", response_model=BucketResponse, summary="获取桶详情")
async def get_bucket(
    bucket_id: str,
    bucket_service: BucketService = Depends(),
):
    """获取存储桶详情。"""
    bucket = await bucket_service.get_bucket(bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="存储桶不存在")
    return bucket


@router.put("/{bucket_id}", response_model=BucketResponse, summary="更新桶配置")
async def update_bucket(
    bucket_id: str,
    data: BucketUpdate,
    bucket_service: BucketService = Depends(),
):
    """更新存储桶配置。"""
    bucket = await bucket_service.update_bucket(bucket_id, data)
    if bucket is None:
        raise HTTPException(status_code=404, detail="存储桶不存在")
    return bucket


@router.delete("/{bucket_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除桶")
async def delete_bucket(
    bucket_id: str,
    force: bool = Query(False),
    bucket_service: BucketService = Depends(),
):
    """删除存储桶。"""
    try:
        await bucket_service.delete_bucket(bucket_id, force=force)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{bucket_id}/stats", response_model=dict, summary="桶统计信息")
async def get_bucket_stats(
    bucket_id: str,
    stats_service=Depends(),
):
    """获取桶统计信息。"""
    stats = await stats_service.get_bucket_stats(bucket_id)
    if stats is None:
        raise HTTPException(status_code=404, detail="存储桶不存在")
    return stats.model_dump()
