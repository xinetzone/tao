"""taolib —— 道可道，非恒道。

本包在仓库根目录从零建立，与 ``apps/chaos`` 下的旧实现互不引用。
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("taolib")
except PackageNotFoundError:  # 直接在源码树中导入、尚无发行版元数据时
    __version__ = "0.0.0"

__all__ = ["__version__"]
