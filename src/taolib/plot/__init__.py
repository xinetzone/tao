"""绘图辅助能力。

当前仅提供 matplotlib 字体配置。matplotlib 不是核心依赖，需要时按
``taolib[plot]`` 额外安装。
"""

from .fonts import (
    DEFAULT_FAMILIES,
    FontConfigError,
    configure_matplotlib_fonts,
    register_font_directory,
)

__all__ = [
    "DEFAULT_FAMILIES",
    "FontConfigError",
    "configure_matplotlib_fonts",
    "register_font_directory",
]