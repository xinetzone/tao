"""Registry 配置读取 — 解析 ``.agents/registry.toml``。"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RegistrySource:
    """单个 Registry 源配置。"""

    name: str  # "local"、"default" 等子表键名
    url: str  # 本地路径或远程 URL
    type: str  # "git" | "http"
    priority: int  # 数值越小越优先
    cache_ttl: int = 3600  # 缓存 TTL（秒），默认 1 小时


def load_registry_config(agents_dir: Path) -> list[RegistrySource]:
    """读取 ``registry.toml`` 并按优先级升序排序返回。

    查找路径为 ``{agents_dir}/registry.toml``。若文件不存在或解析失败，返回空列表。

    Args:
        agents_dir: 承载 ``registry.toml`` 的 ``.agents`` 目录路径。

    Returns:
        按 ``priority`` 升序排列的 :class:`RegistrySource` 列表。
    """
    config_path = agents_dir / "registry.toml"
    if not config_path.exists():
        return []

    try:
        with config_path.open("rb") as f:
            data = tomllib.load(f)
    except OSError, tomllib.TOMLDecodeError:
        return []

    registries_data = data.get("registries", {})
    if not isinstance(registries_data, dict):
        return []

    sources: list[RegistrySource] = []
    for name, entry in registries_data.items():
        if not isinstance(entry, dict):
            continue
        url = entry.get("url", "")
        type_ = entry.get("type", "")
        priority = entry.get("priority", 0)
        cache_ttl = entry.get("cache-ttl", 3600)  # TOML 中用连字符
        sources.append(
            RegistrySource(
                name=name,
                url=url,
                type=type_,
                priority=priority,
                cache_ttl=int(cache_ttl),
            ),
        )

    sources.sort(key=lambda s: s.priority)
    return sources
