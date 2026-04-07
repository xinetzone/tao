"""文件处理协议定义。

定义文件验证和缩略图生成的 Protocol 接口。
"""

from dataclasses import dataclass, field
from typing import Protocol

from taolib.file_storage.models.enums import MediaType, ThumbnailSize


@dataclass(frozen=True, slots=True)
class FileValidationResult:
    """文件验证结果。"""

    valid: bool
    errors: list[str] = field(default_factory=list)
    detected_content_type: str = ""
    media_type: MediaType = MediaType.OTHER


@dataclass(frozen=True, slots=True)
class ThumbnailOutput:
    """缩略图生成输出。"""

    size: ThumbnailSize
    width: int
    height: int
    data: bytes
    content_type: str = "image/webp"


class FileValidatorProtocol(Protocol):
    """文件验证器协议。"""

    async def validate(
        self,
        filename: str,
        declared_content_type: str,
        size_bytes: int,
        header_bytes: bytes,
        allowed_mime_types: list[str] | None = None,
        max_file_size_bytes: int | None = None,
    ) -> FileValidationResult:
        """验证文件。

        Args:
            filename: 文件名
            declared_content_type: 声明的 MIME 类型
            size_bytes: 文件大小
            header_bytes: 文件头部字节（用于 magic byte 检测）
            allowed_mime_types: 允许的 MIME 类型列表（None 表示全部允许）
            max_file_size_bytes: 最大文件大小（None 表示不限制）

        Returns:
            验证结果
        """
        ...


class ThumbnailGeneratorProtocol(Protocol):
    """缩略图生成器协议。"""

    def supports(self, content_type: str) -> bool:
        """检查是否支持该内容类型的缩略图生成。"""
        ...

    async def generate(
        self,
        source_data: bytes,
        content_type: str,
        sizes: list[ThumbnailSize] | None = None,
    ) -> list[ThumbnailOutput]:
        """生成缩略图。

        Args:
            source_data: 原始图片数据
            content_type: MIME 类型
            sizes: 要生成的尺寸列表（None 表示全部规格）

        Returns:
            缩略图输出列表
        """
        ...
