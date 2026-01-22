"""SSH 连接配置读取与脱敏。"""
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict

from .errors import RemoteConfigError


class SshConfig(TypedDict, total=False):
    """SSH 连接配置结构（与 Fabric Connection 的关键字参数兼容）。"""

    host: str
    user: str
    port: int
    connect_kwargs: dict[str, Any]


def _clone_toml_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _clone_toml_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clone_toml_value(v) for v in value]
    return value



@lru_cache(maxsize=16)
def _load_toml_table_from_path(resolved_path: str) -> dict[str, Any]:
    try:
        with Path(resolved_path).open("rb") as file_handle:
            data = tomllib.load(file_handle)
    except tomllib.TOMLDecodeError as exc:
        raise RemoteConfigError(f"SSH 配置文件解析失败：{resolved_path}") from exc
    except OSError as exc:
        raise RemoteConfigError(f"无法读取 SSH 配置文件：{resolved_path}") from exc
    if not isinstance(data, dict):
        raise RemoteConfigError("SSH 配置文件必须解析为 TOML table")
    return data


def load_ssh_config(config_path: str | Path) -> SshConfig:
    """从 TOML 读取 SSH 连接配置（返回深拷贝）。"""
    path = Path(config_path).expanduser().resolve()
    data = _load_toml_table_from_path(str(path))
    return _clone_toml_value(data)


def redact_ssh_config(config: SshConfig | dict[str, Any]) -> dict[str, Any]:
    """脱敏 SSH 配置，避免输出敏感字段。"""
    cloned: dict[str, Any] = _clone_toml_value(dict(config))
    connect_kwargs = cloned.get("connect_kwargs")
    if isinstance(connect_kwargs, dict) and "password" in connect_kwargs:
        connect_kwargs["password"] = "***"
    return cloned


def clear_ssh_config_cache() -> None:
    """清理配置读取缓存（用于测试或动态更新配置文件的场景）。"""
    _load_toml_table_from_path.cache_clear()
