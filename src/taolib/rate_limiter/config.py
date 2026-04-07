"""Configuration loading for rate limiter.

Supports TOML configuration files with environment variable overrides.
"""
import os
from pathlib import Path

from .models import RateLimitConfig

# Default configuration file paths (checked in order)
_DEFAULT_CONFIG_PATHS = [
    Path("rate_limit.toml"),
    Path("config/rate_limit.toml"),
    Path.home() / ".config" / "taolib" / "rate_limit.toml",
    Path(__file__).parent / "rate_limit.toml",  # 模块内默认配置
]


def load_rate_limit_config(config_path: str | None = None) -> RateLimitConfig:
    """加载限流配置。

    按以下顺序查找配置：
    1. 显式指定的 config_path
    2. 环境变量 TAOLIB_RATE_LIMIT_CONFIG
    3. 默认路径列表

    Args:
        config_path: 配置文件路径（可选）

    Returns:
        限流配置实例
    """
    # Check explicit path
    if config_path:
        return RateLimitConfig.from_toml(config_path)

    # Check environment variable
    env_path = os.getenv("TAOLIB_RATE_LIMIT_CONFIG")
    if env_path:
        return RateLimitConfig.from_toml(env_path)

    # Check default paths
    for default_path in _DEFAULT_CONFIG_PATHS:
        if default_path.exists():
            return RateLimitConfig.from_toml(str(default_path))

    # Return default config if no file found
    return _apply_env_overrides(RateLimitConfig())


def _apply_env_overrides(config: RateLimitConfig) -> RateLimitConfig:
    """应用环境变量覆盖。

    环境变量优先级高于配置文件。

    Supported env vars:
        TAOLIB_RATE_LIMIT_ENABLED
        TAOLIB_RATE_LIMIT_DEFAULT_LIMIT
        TAOLIB_RATE_LIMIT_WINDOW_SECONDS
        TAOLIB_RATE_LIMIT_REDIS_URL
    """
    overrides: dict[str, object] = {}

    if (val := os.getenv("TAOLIB_RATE_LIMIT_ENABLED")) is not None:
        overrides["enabled"] = val.lower() in ("true", "1", "yes")

    if (val := os.getenv("TAOLIB_RATE_LIMIT_DEFAULT_LIMIT")) is not None:
        overrides["default_limit"] = int(val)

    if (val := os.getenv("TAOLIB_RATE_LIMIT_WINDOW_SECONDS")) is not None:
        overrides["window_seconds"] = int(val)

    if (val := os.getenv("TAOLIB_RATE_LIMIT_REDIS_URL")) is not None:
        overrides["redis_url"] = val

    if not overrides:
        return config

    return config.model_copy(update=overrides)
