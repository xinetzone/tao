"""测试文件存储模块初始化。"""

from taolib.testing.file_storage import (
    AccessLevel,
    FileStatus,
    FileStorageClient,
    MediaType,
    StorageClass,
    StorageError,
    ThumbnailSize,
    UploadStatus,
    __version__,
)


def test_imports() -> None:
    """测试基本导入。"""
    assert FileStorageClient is not None
    assert StorageError is not None


def test_enums() -> None:
    """测试枚举导入。"""
    assert AccessLevel.PUBLIC == "public"
    assert FileStatus.ACTIVE == "active"
    assert MediaType.IMAGE == "image"
    assert StorageClass.STANDARD == "standard"
    assert ThumbnailSize.SMALL == "small"
    assert UploadStatus.INITIATED == "initiated"


def test_version() -> None:
    """测试版本号。"""
    assert isinstance(__version__, str)
    assert len(__version__) > 0



