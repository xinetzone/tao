"""枚举定义模块。

定义文件存储系统中使用的所有枚举类型。
"""

from enum import StrEnum


class AccessLevel(StrEnum):
    """文件访问级别枚举。"""

    PUBLIC = "public"
    PRIVATE = "private"
    SIGNED_URL = "signed_url"


class FileStatus(StrEnum):
    """文件状态枚举。"""

    PENDING = "pending"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class UploadStatus(StrEnum):
    """上传状态枚举。"""

    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETING = "completing"
    COMPLETED = "completed"
    ABORTED = "aborted"
    EXPIRED = "expired"


class StorageClass(StrEnum):
    """存储类型枚举。"""

    STANDARD = "standard"
    INFREQUENT_ACCESS = "infrequent_access"
    ARCHIVE = "archive"


class ThumbnailSize(StrEnum):
    """缩略图尺寸规格枚举。"""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class MediaType(StrEnum):
    """媒体类型分类枚举。"""

    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    OTHER = "other"


