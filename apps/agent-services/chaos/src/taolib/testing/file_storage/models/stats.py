"""统计数据响应模型。

纯响应模型，无 Document 层（通过聚合查询计算）。
"""

from pydantic import BaseModel, Field


class BucketStatsResponse(BaseModel):
    """存储桶统计响应。"""

    bucket_id: str = Field(..., description="桶 ID")
    bucket_name: str = Field(..., description="桶名称")
    file_count: int = Field(default=0, description="文件数量")
    total_size_bytes: int = Field(default=0, description="总存储大小")
    upload_count: int = Field(default=0, description="上传次数")
    download_count: int = Field(default=0, description="下载次数")


class StorageOverviewResponse(BaseModel):
    """全局存储概览响应。"""

    total_buckets: int = Field(default=0, description="总桶数")
    total_files: int = Field(default=0, description="总文件数")
    total_size_bytes: int = Field(default=0, description="总存储大小")
    active_uploads: int = Field(default=0, description="活跃上传数")


class UploadStatsResponse(BaseModel):
    """上传统计响应。"""

    total_uploads: int = Field(default=0, description="总上传数")
    completed: int = Field(default=0, description="已完成")
    failed: int = Field(default=0, description="已失败")
    in_progress: int = Field(default=0, description="进行中")
    total_bytes_uploaded: int = Field(default=0, description="总上传字节数")


