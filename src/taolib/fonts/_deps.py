"""私有依赖垫片：延迟导入 matplotlib。

matplotlib 不是 ``taolib`` 的强制依赖，导入放在调用点，缺失时给出可操作的提示。
"""

from typing import Any

from .errors import FontConfigError

__all__ = ["require_matplotlib"]


def require_matplotlib() -> tuple[Any, Any]:
    """返回 ``(font_manager, rcParams)``；未安装 matplotlib 时抛错。"""
    try:
        from matplotlib import font_manager, rcParams
    except ImportError as exc:
        raise FontConfigError("配置 matplotlib 字体需要 matplotlib，请安装 taolib[fonts]") from exc
    return font_manager, rcParams
