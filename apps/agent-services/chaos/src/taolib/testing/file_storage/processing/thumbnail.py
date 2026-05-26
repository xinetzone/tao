"""缩略图生成器。

使用 Pillow 生成多种规格的缩略图。
"""

import asyncio
import io

from taolib.testing.file_storage.models.enums import ThumbnailSize
from taolib.testing.file_storage.processing.protocols import ThumbnailOutput

# 缩略图尺寸映射
THUMBNAIL_DIMENSIONS: dict[ThumbnailSize, tuple[int, int]] = {
    ThumbnailSize.SMALL: (150, 150),
    ThumbnailSize.MEDIUM: (400, 400),
    ThumbnailSize.LARGE: (800, 800),
}

# 支持的图片 MIME 类型
SUPPORTED_IMAGE_TYPES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }
)


class PillowThumbnailGenerator:
    """基于 Pillow 的缩略图生成器。"""

    def supports(self, content_type: str) -> bool:
        """检查是否支持该内容类型。"""
        return content_type in SUPPORTED_IMAGE_TYPES

    async def generate(
        self,
        source_data: bytes,
        content_type: str,
        sizes: list[ThumbnailSize] | None = None,
    ) -> list[ThumbnailOutput]:
        """生成缩略图（在线程池中执行 CPU 密集操作）。"""
        if not self.supports(content_type):
            return []

        target_sizes = sizes or list(ThumbnailSize)
        return await asyncio.to_thread(self._generate_sync, source_data, target_sizes)

    def _generate_sync(
        self,
        source_data: bytes,
        sizes: list[ThumbnailSize],
    ) -> list[ThumbnailOutput]:
        """同步生成缩略图。"""
        from PIL import Image

        results: list[ThumbnailOutput] = []
        source_image = Image.open(io.BytesIO(source_data))

        # 转换为 RGB（处理 RGBA 和 P 模式）
        if source_image.mode in ("RGBA", "P"):
            source_image = source_image.convert("RGBA")
            background = Image.new("RGBA", source_image.size, (255, 255, 255, 255))
            background.paste(source_image, mask=source_image.split()[3])
            source_image = background.convert("RGB")
        elif source_image.mode != "RGB":
            source_image = source_image.convert("RGB")

        for size in sizes:
            dimensions = THUMBNAIL_DIMENSIONS[size]
            thumb = source_image.copy()
            thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)

            output_buffer = io.BytesIO()
            thumb.save(output_buffer, format="WEBP", quality=85)
            thumb_data = output_buffer.getvalue()

            results.append(
                ThumbnailOutput(
                    size=size,
                    width=thumb.width,
                    height=thumb.height,
                    data=thumb_data,
                    content_type="image/webp",
                )
            )

        return results


