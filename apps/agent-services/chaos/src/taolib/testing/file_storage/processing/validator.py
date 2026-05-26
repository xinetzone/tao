"""默认文件验证器。

实现 FileValidatorProtocol，提供 MIME 检测、大小验证和安全检查。
"""

import mimetypes

from taolib.testing.file_storage.models.enums import MediaType
from taolib.testing.file_storage.processing.protocols import FileValidationResult

# 危险 MIME 类型黑名单
_DANGEROUS_MIME_TYPES = frozenset(
    {
        "application/x-executable",
        "application/x-sharedlib",
        "application/x-msdos-program",
        "application/x-msdownload",
        "application/x-dosexec",
        "application/vnd.microsoft.portable-executable",
    }
)

# 常见 magic bytes 签名映射
_MAGIC_SIGNATURES: list[tuple[bytes, str]] = [
    # 图片
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),  # RIFF....WEBP
    # 视频
    (b"\x00\x00\x00\x18ftypmp4", "video/mp4"),
    (b"\x00\x00\x00\x1cftypmp4", "video/mp4"),
    (b"\x00\x00\x00\x20ftypmp4", "video/mp4"),
    (b"\x00\x00\x00\x18ftypisom", "video/mp4"),
    (b"\x00\x00\x00\x1cftypisom", "video/mp4"),
    (b"RIFF", "video/avi"),  # RIFF....AVI
    # 文档
    (b"%PDF", "application/pdf"),
    (b"PK\x03\x04", "application/zip"),
]

# MIME 类型 → MediaType 映射
_MEDIA_TYPE_MAP: dict[str, MediaType] = {
    "image": MediaType.IMAGE,
    "video": MediaType.VIDEO,
    "audio": MediaType.AUDIO,
    "application/pdf": MediaType.DOCUMENT,
    "application/msword": MediaType.DOCUMENT,
    "application/vnd.openxmlformats-officedocument": MediaType.DOCUMENT,
    "text": MediaType.DOCUMENT,
}


def _detect_content_type(header_bytes: bytes, filename: str) -> str:
    """通过 magic bytes 和文件扩展名检测 MIME 类型。"""
    # 优先通过 magic bytes 检测
    for signature, mime_type in _MAGIC_SIGNATURES:
        if header_bytes.startswith(signature):
            # RIFF 格式需要进一步判断
            if signature == b"RIFF" and len(header_bytes) >= 12:
                sub_type = header_bytes[8:12]
                if sub_type == b"WEBP":
                    return "image/webp"
                if sub_type == b"AVI ":
                    return "video/avi"
                continue
            return mime_type

    # 回退到扩展名检测
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"


def _classify_media_type(content_type: str) -> MediaType:
    """将 MIME 类型分类为 MediaType。"""
    # 精确匹配
    if content_type in _MEDIA_TYPE_MAP:
        return _MEDIA_TYPE_MAP[content_type]

    # 前缀匹配
    main_type = content_type.split("/")[0]
    if main_type in _MEDIA_TYPE_MAP:
        return _MEDIA_TYPE_MAP[main_type]

    # 特殊前缀
    if content_type.startswith("application/vnd.openxmlformats"):
        return MediaType.DOCUMENT

    return MediaType.OTHER


class DefaultFileValidator:
    """默认文件验证器实现。"""

    async def validate(
        self,
        filename: str,
        declared_content_type: str,
        size_bytes: int,
        header_bytes: bytes,
        allowed_mime_types: list[str] | None = None,
        max_file_size_bytes: int | None = None,
    ) -> FileValidationResult:
        """验证文件的类型、大小和安全性。"""
        errors: list[str] = []

        # 检测实际 MIME 类型
        detected_type = _detect_content_type(header_bytes, filename)

        # 安全检查：黑名单
        if detected_type in _DANGEROUS_MIME_TYPES:
            errors.append(f"检测到危险文件类型: {detected_type}")

        # 大小验证
        if max_file_size_bytes and size_bytes > max_file_size_bytes:
            errors.append(
                f"文件大小 {size_bytes} 字节超出限制 {max_file_size_bytes} 字节"
            )

        # MIME 白名单检查
        if allowed_mime_types:
            if detected_type not in allowed_mime_types:
                errors.append(f"文件类型 {detected_type} 不在允许列表中")

        # 分类媒体类型
        media_type = _classify_media_type(detected_type)

        return FileValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            detected_content_type=detected_type,
            media_type=media_type,
        )


