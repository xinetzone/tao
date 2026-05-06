"""Symphony TOML 配置加载器。

使用标准库 tomllib 解析 symphony.toml 文件，
仅读取 [defaults] 段用于配置合并。
"""

import tomllib
from pathlib import Path

from taolib.symphony.errors import ConfigError


def load_toml(path: Path) -> dict:
    """从 symphony.toml 文件加载 [defaults] 段。

    Args:
        path: symphony.toml 文件路径。

    Returns:
        [defaults] 段的字典，如果文件中没有 [defaults] 段则返回空字典。

    Raises:
        ConfigError: 文件无法读取或 TOML 解析失败。
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"无法读取 TOML 配置文件: {path}"
        raise ConfigError(msg) from exc

    try:
        data = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        msg = f"TOML 解析失败 ({path}): {exc}"
        raise ConfigError(msg) from exc

    if not isinstance(data, dict):
        msg = f"TOML 根元素必须是表，实际类型为 {type(data).__name__} ({path})"
        raise ConfigError(msg)

    # 只读取 [defaults] 段
    defaults = data.get("defaults")
    if defaults is None:
        return {}

    if not isinstance(defaults, dict):
        msg = (
            f"[defaults] 段必须是表，实际类型为 {type(defaults).__name__} ({path})"
        )
        raise ConfigError(msg)

    return dict(defaults)
