"""测试文件处理管道。"""

import pytest

from taolib.testing.file_storage.errors import FileValidationError
from taolib.testing.file_storage.models.enums import MediaType
from taolib.testing.file_storage.processing.pipeline import ProcessingPipeline
from taolib.testing.file_storage.processing.validator import DefaultFileValidator


class TestFileValidator:
    """测试文件验证器。"""

    @pytest.fixture
    def validator(self) -> DefaultFileValidator:
        return DefaultFileValidator()

    @pytest.mark.asyncio
    async def test_valid_jpeg(self, validator: DefaultFileValidator) -> None:
        # JPEG magic bytes: \xff\xd8\xff
        header = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        result = await validator.validate(
            filename="photo.jpg",
            declared_content_type="image/jpeg",
            size_bytes=len(header),
            header_bytes=header,
        )
        assert result.valid is True
        assert result.detected_content_type == "image/jpeg"
        assert result.media_type == MediaType.IMAGE

    @pytest.mark.asyncio
    async def test_valid_png(self, validator: DefaultFileValidator) -> None:
        # PNG magic bytes: \x89PNG\r\n\x1a\n
        header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        result = await validator.validate(
            filename="image.png",
            declared_content_type="image/png",
            size_bytes=len(header),
            header_bytes=header,
        )
        assert result.valid is True
        assert result.detected_content_type == "image/png"

    @pytest.mark.asyncio
    async def test_size_limit_exceeded(self, validator: DefaultFileValidator) -> None:
        result = await validator.validate(
            filename="large.bin",
            declared_content_type="application/octet-stream",
            size_bytes=1000,
            header_bytes=b"\x00" * 100,
            max_file_size_bytes=500,
        )
        assert result.valid is False
        assert any("大小" in e for e in result.errors)

    @pytest.mark.asyncio
    async def test_mime_whitelist_reject(self, validator: DefaultFileValidator) -> None:
        result = await validator.validate(
            filename="video.mp4",
            declared_content_type="video/mp4",
            size_bytes=100,
            header_bytes=b"\x00" * 100,
            allowed_mime_types=["image/jpeg", "image/png"],
        )
        assert result.valid is False
        assert any("允许" in e for e in result.errors)

    @pytest.mark.asyncio
    async def test_pdf_detection(self, validator: DefaultFileValidator) -> None:
        header = b"%PDF-1.4" + b"\x00" * 100
        result = await validator.validate(
            filename="document.pdf",
            declared_content_type="application/pdf",
            size_bytes=len(header),
            header_bytes=header,
        )
        assert result.valid is True
        assert result.media_type == MediaType.DOCUMENT

    @pytest.mark.asyncio
    async def test_unknown_type(self, validator: DefaultFileValidator) -> None:
        result = await validator.validate(
            filename="unknown.xyz",
            declared_content_type="application/octet-stream",
            size_bytes=50,
            header_bytes=b"\x00" * 50,
        )
        assert result.valid is True
        assert result.media_type == MediaType.OTHER


class TestProcessingPipeline:
    """测试处理管道。"""

    @pytest.fixture
    def pipeline(self) -> ProcessingPipeline:
        validator = DefaultFileValidator()
        return ProcessingPipeline(validator=validator)

    @pytest.mark.asyncio
    async def test_process_valid_file(self, pipeline: ProcessingPipeline) -> None:
        data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        result = await pipeline.process_upload(
            filename="photo.jpg",
            declared_content_type="image/jpeg",
            data=data,
        )
        assert result.validated_content_type == "image/jpeg"
        assert result.media_type == MediaType.IMAGE
        assert result.size_bytes == len(data)
        assert len(result.checksum_sha256) == 64  # SHA-256 hex length

    @pytest.mark.asyncio
    async def test_process_invalid_file(self, pipeline: ProcessingPipeline) -> None:
        data = b"small" * 10
        with pytest.raises(FileValidationError):
            await pipeline.process_upload(
                filename="too-big.txt",
                declared_content_type="text/plain",
                data=data,
                max_file_size_bytes=1,
            )

    @pytest.mark.asyncio
    async def test_generate_thumbnails_no_generator(
        self, pipeline: ProcessingPipeline
    ) -> None:
        # 没有缩略图生成器时返回空列表
        result = await pipeline.generate_thumbnails(b"\x00", "image/jpeg")
        assert result == []



