"""字体子系统：发现、注册与后端生效。

字体是跨图表、文档、PDF 等场景的通用资源，因此置于包顶层；matplotlib 只是
当前唯一的落地后端，按需延迟导入。

分层结构（下层不反向依赖上层）::

    errors      异常类型
    discovery   与后端无关的字体文件发现（前置闸）
    registry    幂等注册到后端字体管理器（注册闸）
    _deps       延迟导入垫片，供 registry / 后端模块共用
    matplotlib  写 rcParams 并反查生效（生效闸）

新增后端（reportlab、PIL、CSS 等）时，在 ``fonts/`` 下加同层模块，复用
``iter_font_files`` / ``register_font_directory``，并在此处导出其公开函数。

实现遵循三道闸门：

1. **前置闸**：字体目录必须存在、是目录且至少含一个字体文件；
2. **注册闸**：注册前按规范化路径去重，重复调用不会让 ``ttflist`` 持续膨胀；
3. **生效闸**：写入 rcParams 后用 ``findfont(..., fallback_to_default=False)``
   反查，解析不到任何家族即抛 :class:`FontConfigError`，不把"写入成功"
   当作"字体可用"。

matplotlib 不是 ``taolib`` 的强制依赖：缺失时抛 :class:`FontConfigError` 并提示
安装 ``taolib[fonts]``。
"""

from .discovery import FONT_EXTENSIONS, iter_font_files
from .errors import FontConfigError
from .matplotlib import DEFAULT_FAMILIES, configure_matplotlib_fonts
from .registry import register_font_directory

__all__ = [
    "DEFAULT_FAMILIES",
    "FONT_EXTENSIONS",
    "FontConfigError",
    "configure_matplotlib_fonts",
    "iter_font_files",
    "register_font_directory",
]
