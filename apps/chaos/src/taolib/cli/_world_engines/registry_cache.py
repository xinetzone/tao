"""Registry 缓存管理 — 远程 Git Index 的本地缓存与 TTL 控制。"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

# 默认 TTL（秒）
DEFAULT_TTL = 3600


def inject_token(url: str) -> str:
    """将 WORLD_TOKEN 注入 HTTPS Git URL。

    格式：https://github.com/org/repo → https://x-access-token:{token}@github.com/org/repo
    非 HTTPS URL（SSH、本地路径等）不注入。
    """
    token = os.environ.get("WORLD_TOKEN", "").strip()
    if not token:
        return url
    if not url.startswith("https://"):
        return url
    return url.replace("https://", f"https://x-access-token:{token}@", 1)


@dataclass(frozen=True)
class CacheConfig:
    """缓存配置。"""

    cache_dir: Path  # 缓存根目录
    ttl: int  # TTL 秒数
    offline: bool  # 离线模式
    force_update: bool  # 强制更新（忽略 TTL）


def _default_cache_dir() -> Path:
    """获取默认缓存目录。

    优先使用 WORLD_CACHE_DIR 环境变量；
    未设置时在 Windows 使用 %LOCALAPPDATA%/agentforge/registry，
    其他系统使用 ~/.cache/agentforge/registry。
    """
    env_dir = os.environ.get("WORLD_CACHE_DIR", "").strip()
    if env_dir:
        return Path(env_dir)
    # Windows: LOCALAPPDATA，其他: ~/.cache
    local_app = os.environ.get("LOCALAPPDATA", "")
    if local_app:
        return Path(local_app) / "agentforge" / "registry"
    return Path.home() / ".cache" / "agentforge" / "registry"


def get_cache_config(ttl: int = DEFAULT_TTL, force_update: bool = False) -> CacheConfig:
    """构建缓存配置，读取环境变量。

    环境变量：
    - WORLD_CACHE_DIR：覆盖默认缓存目录
    - WORLD_OFFLINE：设为 "true" 或 "1" 启用离线模式
    """
    cache_dir = _default_cache_dir()
    offline_env = os.environ.get("WORLD_OFFLINE", "").strip().lower()
    offline = offline_env in ("true", "1")
    return CacheConfig(
        cache_dir=cache_dir,
        ttl=ttl,
        offline=offline,
        force_update=force_update,
    )


def _is_cache_fresh(cache_path: Path, ttl: int) -> bool:
    """检查缓存是否在 TTL 有效期内。

    策略：检查 .git/FETCH_HEAD 的 mtime（优先）；
    如果不存在则检查 .git/HEAD 的 mtime。
    """
    # 优先用 FETCH_HEAD（fetch 后更新）
    fetch_head = cache_path / ".git" / "FETCH_HEAD"
    if fetch_head.exists():
        mtime = fetch_head.stat().st_mtime
    else:
        head = cache_path / ".git" / "HEAD"
        if not head.exists():
            return False
        mtime = head.stat().st_mtime
    return (time.time() - mtime) < ttl


def _clone_index(url: str, dest: Path) -> bool:
    """首次 clone Index 仓库到 dest。

    使用 git clone --depth 1。失败时返回 False，不抛异常。
    WORLD_TOKEN 环境变量存在时自动注入认证信息。
    """
    authed_url = inject_token(url)
    cmd = ["git", "clone", "--depth", "1", authed_url, str(dest)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            if "Authentication" in stderr or "could not read Username" in stderr:
                # 认证相关错误，静默降级
                pass
            return False
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def _fetch_index(cache_path: Path) -> bool:
    """增量更新已缓存的 Index。

    获取 remote URL 后注入 WORLD_TOKEN，执行 git fetch --depth 1，
    然后 git reset --hard FETCH_HEAD。
    失败时返回 False（降级使用旧缓存）。
    """
    # 获取当前 remote URL
    get_url_cmd = ["git", "-C", str(cache_path), "remote", "get-url", "origin"]
    try:
        url_result = subprocess.run(
            get_url_cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if url_result.returncode != 0:
            return False
        original_url = url_result.stdout.strip()
    except FileNotFoundError, subprocess.TimeoutExpired, OSError:
        return False

    authed_url = inject_token(original_url)
    fetch_cmd = ["git", "-C", str(cache_path), "fetch", "--depth", "1", authed_url]
    try:
        result = subprocess.run(
            fetch_cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            return False
    except FileNotFoundError, subprocess.TimeoutExpired, OSError:
        return False

    reset_cmd = ["git", "-C", str(cache_path), "reset", "--hard", "FETCH_HEAD"]
    try:
        result = subprocess.run(
            reset_cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError, subprocess.TimeoutExpired, OSError:
        return False


def ensure_index_cache(
    registry_name: str,
    registry_url: str,
    config: CacheConfig,
) -> Path | None:
    """确保远程 Registry Index 的本地缓存可用。

    决策矩阵：
    - 离线模式 + 缓存已存在 → 直接返回（无论 TTL）
    - 离线模式 + 缓存不存在 → 返回 None
    - 缓存已存在 + 未过期 + 非强制更新 → 直接返回
    - 缓存已存在 + (已过期 或 强制更新) → fetch 后返回
    - 缓存不存在 → clone 后返回

    Args:
        registry_name: Registry 源名称（用作子目录名）。
        registry_url: 远程 Git URL。
        config: 缓存配置。

    Returns:
        本地 Index 缓存目录路径，不可用时返回 None。
    """
    cache_path = config.cache_dir / registry_name

    # 缓存已存在
    if cache_path.exists() and (cache_path / ".git").is_dir():
        if config.offline:
            return cache_path
        if not config.force_update and _is_cache_fresh(cache_path, config.ttl):
            return cache_path
        # 过期或强制更新：增量 fetch
        _fetch_index(cache_path)
        return cache_path

    # 缓存不存在
    if config.offline:
        return None

    # 确保父目录存在
    config.cache_dir.mkdir(parents=True, exist_ok=True)

    if _clone_index(registry_url, cache_path):
        return cache_path
    return None
