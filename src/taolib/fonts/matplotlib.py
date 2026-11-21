"""matplotlib 后端（生效闸）：把可解析的字体家族写入 rcParams。

matplotlib 只是字体的一个落地目标。新增后端（reportlab、PIL、CSS 等）时，
在 ``fonts/`` 下新增同层模块并复用 :mod:`taolib.fonts.discovery` 与
:mod:`taolib.fonts.registry`，无需改动本模块。
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ._deps import require_matplotlib
from .errors import FontConfigError
from .registry import register_font_directory

__all__ = ["DEFAULT_FAMILIES", "configure_matplotlib_fonts"]

#: 默认候选家族；调用方可按需覆盖。
DEFAULT_FAMILIES: tuple[str, ...] = ("Maple Mono NF CN",)


def _resolvable(font_manager: Any, family: str) -> bool:
    """按 ``fallback_to_default=False`` 反查，能解析即为真。"""
    try:
        font_manager.findfont(
            font_manager.FontProperties(family=family),
            fallback_to_default=False,
        )
    except ValueError:
        return False
    return True


def configure_matplotlib_fonts(
    font_directory: str | Path | None = None,
    families: Sequence[str] = DEFAULT_FAMILIES,
    *,
    unicode_minus: bool = False,
) -> tuple[str, ...]:
    """注册字体目录并把可解析的家族设为 matplotlib 默认无衬线字体。

    Args:
        font_directory: 字体目录；``None`` 表示不注册新字体，只在已安装字体中查找。
        families: 候选家族名，按优先级排列。
        unicode_minus: 是否用 U+2212 绘制负号。默认 ``False``，避免所选 CJK
            字体不含该码位时负号显示为方框。

    Returns:
        实际生效的家族名，按 ``families`` 顺序且只保留能解析的项。

    Raises:
        FontConfigError: 目录不可用，或所有候选家族均无法解析。
    """
    if font_directory is not None:
        register_font_directory(font_directory)

    font_manager, rcParams = require_matplotlib()

    resolved = tuple(name for name in families if _resolvable(font_manager, name))
    if not resolved:
        raise FontConfigError(f"候选字体家族均无法解析：{list(families)}")

    rcParams["font.family"] = ["sans-serif"]
    rcParams["font.sans-serif"] = list(resolved)
    rcParams["axes.unicode_minus"] = unicode_minus
    return resolved
