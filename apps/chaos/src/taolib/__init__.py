"""taolib：AgentForge 项目的 AI 智能体集成库。

本包依道家“极致简约、大道至简”理念组织能力，按领域拆分为多个子模块，
例如 :mod:`taolib.github_app` 负责 GitHub App 安装令牌管理，
:mod:`taolib.cli` 提供与之对应的命令行入口。
调用方应从各子模块的公共接口导入能力，避免依赖内部模块。
"""

from __future__ import annotations

# 版本号统一由 pdm-backend 的 SCM 源派生，构建时写入 ``_version.py``。
# 详见 ``pyproject.toml`` 中的 ``[tool.pdm.version]`` 段与
# ``docs/tech/build-conventions.md`` 的版本管理章节。
try:
    from ._version import __version__
except ImportError:  # pragma: no cover - 源码树直接运行（未构建安装）时的兜底
    try:
        from importlib.metadata import PackageNotFoundError
        from importlib.metadata import version as _pkg_version

        try:
            __version__ = _pkg_version("taolib")
        except PackageNotFoundError:
            __version__ = "0.0.0+unknown"
    except ImportError:
        __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
