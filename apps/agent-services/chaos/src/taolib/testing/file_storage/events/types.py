"""事件类型定义。

定义文件存储系统的事件数据类。
"""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class FileUploadedEvent:
    """文件上传完成事件。"""

    file_id: str
    bucket_id: str
    object_key: str
    content_type: str
    size_bytes: int
    uploaded_by: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """转换为字典。"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = "file.uploaded"
        return data


@dataclass(frozen=True, slots=True)
class FileDeletedEvent:
    """文件删除事件。"""

    file_id: str
    bucket_id: str
    object_key: str
    deleted_by: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """转换为字典。"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = "file.deleted"
        return data


@dataclass(frozen=True, slots=True)
class UploadSessionCompletedEvent:
    """上传会话完成事件。"""

    session_id: str
    file_id: str
    total_chunks: int
    total_bytes: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """转换为字典。"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = "upload.completed"
        return data


@dataclass(frozen=True, slots=True)
class BucketCreatedEvent:
    """存储桶创建事件。"""

    bucket_id: str
    bucket_name: str
    created_by: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """转换为字典。"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = "bucket.created"
        return data


@dataclass(frozen=True, slots=True)
class FileExpiredEvent:
    """文件过期事件。"""

    file_id: str
    bucket_id: str
    expired_at: datetime
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """转换为字典。"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["expired_at"] = self.expired_at.isoformat()
        data["event_type"] = "file.expired"
        return data


