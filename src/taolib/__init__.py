"""
AgentForge - AI Agents framework
"""

from importlib.metadata import PackageNotFoundError, version as _dist_version
import sys
import warnings


def version() -> str:
    try:
        return _dist_version("taolib")
    except PackageNotFoundError:
        return "0+unknown"


def __getattr__(name: str):
    if name == "__version__":
        if sys.version_info >= (3, 16):
            warnings.warn(
                "taolib.__version__ 将在后续版本中弃用；请改用 taolib.version() 或 "
                "importlib.metadata.version('taolib')。",
                DeprecationWarning,
                stacklevel=2,
            )
        return version()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | {"__version__"})
