"""文件处理模块。

导出处理协议和实现。
"""

from taolib.file_storage.processing.pipeline import (
    ProcessingPipeline,
    ProcessingResult,
)
from taolib.file_storage.processing.protocols import (
    FileValidationResult,
    FileValidatorProtocol,
    ThumbnailGeneratorProtocol,
    ThumbnailOutput,
)
from taolib.file_storage.processing.validator import DefaultFileValidator

__all__ = [
    "DefaultFileValidator",
    "FileValidationResult",
    "FileValidatorProtocol",
    "ProcessingPipeline",
    "ProcessingResult",
    "ThumbnailGeneratorProtocol",
    "ThumbnailOutput",
]
