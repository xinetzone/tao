"""字体注册（注册闸）：幂等地把字体文件加入 matplotlib 字体管理器。"""

import logging
import os
from pathlib import Path

from ._deps import require_matplotlib
from .discovery import iter_font_files
from .errors import FontConfigError

__all__ = ["register_font_directory"]

logger = logging.getLogger(__name__)

#: 已注册文件的规范化绝对路径，用于跨调用去重。
_registered: set[str] = set()


def register_font_directory(directory: str | Path) -> list[Path]:
    """注册目录（含子目录）内的全部字体文件，返回本次新注册的文件。

    已注册过的文件按规范化绝对路径跳过，因此可安全重复调用（顺序调用）。

    Args:
        directory: 字体目录。

    Returns:
        本次真正新增到 matplotlib 字体管理器的文件路径列表。

    Raises:
        FontConfigError: 目录不存在、不是目录、没有字体文件，或全部加载失败。
    """
    files = iter_font_files(directory)
    font_manager, _ = require_matplotlib()

    added: list[Path] = []
    already_known = 0
    for file in files:
        key = os.path.normcase(str(file.resolve()))
        if key in _registered:
            already_known += 1
            continue
        try:
            font_manager.fontManager.addfont(str(file))
        except Exception as exc:  # 单个字体损坏时跳过，整体可用性由生效闸兜底
            logger.error("字体加载失败，已跳过：%s（%s）", file, exc)
            continue
        _registered.add(key)
        added.append(file)

    if not added and not already_known:
        raise FontConfigError(f"字体目录中的字体全部加载失败：{directory}")
    return added
