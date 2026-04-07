"""统计服务。

提供存储统计聚合查询。
"""

from taolib.file_storage.models.enums import FileStatus, UploadStatus
from taolib.file_storage.models.stats import (
    BucketStatsResponse,
    StorageOverviewResponse,
    UploadStatsResponse,
)
from taolib.file_storage.repository.bucket_repo import BucketRepository
from taolib.file_storage.repository.file_repo import FileRepository
from taolib.file_storage.repository.upload_repo import UploadSessionRepository


class StatsService:
    """统计服务。"""

    def __init__(
        self,
        bucket_repo: BucketRepository,
        file_repo: FileRepository,
        upload_repo: UploadSessionRepository,
    ) -> None:
        self._bucket_repo = bucket_repo
        self._file_repo = file_repo
        self._upload_repo = upload_repo

    async def get_bucket_stats(self, bucket_id: str) -> BucketStatsResponse | None:
        """获取存储桶统计。"""
        bucket = await self._bucket_repo.get_by_id(bucket_id)
        if bucket is None:
            return None

        upload_count = await self._upload_repo.count(
            {"bucket_id": bucket_id, "status": UploadStatus.COMPLETED}
        )

        return BucketStatsResponse(
            bucket_id=bucket.id,
            bucket_name=bucket.name,
            file_count=bucket.file_count,
            total_size_bytes=bucket.total_size_bytes,
            upload_count=upload_count,
            download_count=0,
        )

    async def get_storage_overview(self) -> StorageOverviewResponse:
        """获取全局存储概览。"""
        total_buckets = await self._bucket_repo.count()
        total_files = await self._file_repo.count(
            {"status": {"$ne": FileStatus.DELETED}}
        )

        # 聚合总大小
        buckets = await self._bucket_repo.list(limit=10000)
        total_size = sum(b.total_size_bytes for b in buckets)

        active_uploads = await self._upload_repo.count(
            {
                "status": {
                    "$in": [
                        UploadStatus.INITIATED,
                        UploadStatus.IN_PROGRESS,
                    ]
                }
            }
        )

        return StorageOverviewResponse(
            total_buckets=total_buckets,
            total_files=total_files,
            total_size_bytes=total_size,
            active_uploads=active_uploads,
        )

    async def get_upload_stats(self) -> UploadStatsResponse:
        """获取上传统计。"""
        total = await self._upload_repo.count()
        completed = await self._upload_repo.count({"status": UploadStatus.COMPLETED})
        failed = await self._upload_repo.count({"status": UploadStatus.ABORTED})
        in_progress = await self._upload_repo.count(
            {
                "status": {
                    "$in": [
                        UploadStatus.INITIATED,
                        UploadStatus.IN_PROGRESS,
                    ]
                }
            }
        )

        # 统计已上传总字节数
        sessions = await self._upload_repo.list(
            filters={"status": UploadStatus.COMPLETED}, limit=10000
        )
        total_bytes = sum(s.uploaded_bytes for s in sessions)

        return UploadStatsResponse(
            total_uploads=total,
            completed=completed,
            failed=failed,
            in_progress=in_progress,
            total_bytes_uploaded=total_bytes,
        )
