"""文件存储自定义异常。

定义文件存储系统中使用的异常层次结构。
"""


class StorageError(Exception):
    """所有存储错误的基类。"""


class FileNotFoundError_(StorageError):
    """文件不存在。"""


class BucketNotFoundError(StorageError):
    """存储桶不存在。"""


class BucketNotEmptyError(StorageError):
    """存储桶非空，无法删除。"""


class UploadSessionNotFoundError(StorageError):
    """上传会话不存在。"""


class UploadSessionExpiredError(StorageError):
    """上传会话已过期。"""


class FileValidationError(StorageError):
    """文件验证失败（MIME/大小/格式）。"""


class StorageBackendError(StorageError):
    """后端存储操作失败。"""


class CDNError(StorageError):
    """CDN 操作失败。"""


class AccessDeniedError(StorageError):
    """访问被拒绝。"""


class QuotaExceededError(StorageError):
    """超出配额限制。"""


class ChunkMismatchError(StorageError):
    """分片校验和不匹配或索引越界。"""


class DuplicateObjectError(StorageError):
    """对象键已存在。"""


class SignedUrlError(StorageError):
    """签名 URL 验证失败。"""
