"""与后端无关的字体文件发现（前置闸）。

本模块不依赖任何渲染后端，后续接入 reportlab、PIL、CSS ``@font-face`` 等
目标时可直接复用。
"""

from pathlib import Path

from .errors import FontConfigError

__all__ = ["FONT_EXTENSIONS", "iter_font_files"]

#: 可被主流后端识别的字体文件扩展名。
FONT_EXTENSIONS = frozenset({".ttf", ".otf", ".ttc", ".otc"})


def iter_font_files(directory: str | Path) -> list[Path]:
    """递归发现目录（含子目录）内的字体文件。

    Args:
        directory: 字体目录。

    Returns:
        按路径排序的字体文件列表，保证同一目录多次扫描结果稳定。

    Raises:
        FontConfigError: 目录不存在、不是目录，或其中没有任何字体文件。
    """
    root = Path(directory)
    if not root.is_dir():
        raise FontConfigError(f"字体目录不存在或不是目录：{root}")

    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in FONT_EXTENSIONS
    )
    if not files:
        raise FontConfigError(f"字体目录中没有字体文件：{root}")
    return files
