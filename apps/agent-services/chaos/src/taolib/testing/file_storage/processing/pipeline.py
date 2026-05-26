"""文件处理管道。

编排文件验证、存储和缩略图生成流程。
"""

import hashlib
from dataclasses import dataclass

from taolib.testing.file_storage.errors import FileValidationError
from taolib.testing.file_storage.models.enums import MediaType, ThumbnailSize
from taolib.testing.file_storage.processing.protocols import (
    FileValidationResult,
    FileValidatorProtocol,
    ThumbnailGeneratorProtocol,
    ThumbnailOutput,
)


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    """文件处理结果。"""

    validated_content_type: str
    media_type: MediaType
    checksum_sha256: str
    size_bytes: int


class ProcessingPipeline:
    """文件处理管道。

    编排验证和后处理步骤。
    """

    def __init__(
        self,
        validator: FileValidatorProtocol,
        thumbnail_generator: ThumbnailGeneratorProtocol | None = None,
    ) -> None:
        self._validator = validator
        self._thumbnail_generator = thumbnail_generator

    async def process_upload(
        self,
        filename: str,
        declared_content_type: str,
        data: bytes,
        allowed_mime_types: list[str] | None = None,
        max_file_size_bytes: int | None = None,
    ) -> ProcessingResult:
        """处理上传的文件。

        执行验证并计算校验和。

        Args:
            filename: 文件名
            declared_content_type: 声明的 MIME 类型
            data: 文件数据
            allowed_mime_types: 允许的 MIME 类型
            max_file_size_bytes: 最大文件大小

        Returns:
            处理结果

        Raises:
            FileValidationError: 如果验证失败
        """
        # 获取头部字节进行 magic byte 检测
        header_bytes = data[:8192]

        # 验证文件
        result: FileValidationResult = await self._validator.validate(
            filename=filename,
            declared_content_type=declared_content_type,
            size_bytes=len(data),
            header_bytes=header_bytes,
            allowed_mime_types=allowed_mime_types,
            max_file_size_bytes=max_file_size_bytes,
        )

        if not result.valid:
            raise FileValidationError(f"文件验证失败: {'; '.join(result.errors)}")

        # 计算 SHA-256 校验和
        checksum = hashlib.sha256(data).hexdigest()

        return ProcessingResult(
            validated_content_type=result.detected_content_type,
            media_type=result.media_type,
            checksum_sha256=checksum,
            size_bytes=len(data),
        )

    async def generate_thumbnails(
        self,
        data: bytes,
        content_type: str,
        sizes: list[ThumbnailSize] | None = None,
    ) -> list[ThumbnailOutput]:
        """生成缩略图。

        Args:
            data: 原始文件数据
            content_type: MIME 类型
            sizes: 要生成的尺寸列表

        Returns:
            缩略图输出列表
        """
        if self._thumbnail_generator is None:
            return []
        if not self._thumbnail_generator.supports(content_type):
            return []
        return await self._thumbnail_generator.generate(data, content_type, sizes)


