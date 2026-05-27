"""taolib - 道可道，非恒道。

提供文档构建自动化、远程 SSH 探测与 Matplotlib 字体配置功能。
"""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # type: ignore[import-not-found]

try:
    __version__ = version("taolib")
except Exception:
    import os

    __version__ = os.environ.get("TAOLIB_VERSION", "0.0.0")
