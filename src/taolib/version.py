"""版本信息工具

这是一个独立的版本信息工具模块，可以被其他包导入和使用。
它提供了从pyproject.toml文件或已安装的包元数据中读取版本信息的功能。

功能:
- 从pyproject.toml文件中读取版本信息
- 从已安装的包元数据中获取版本信息
- 提供命令行接口获取版本号

示例用法:
    # 作为模块导入
    from taolib.version import get_version, __version__
    
    # 获取版本号
    version = get_version()
    print(f"版本号: {version}")
    
    # 直接使用版本变量
    print(f"版本号: {__version__}")
    
    # 从命令行运行
    # python -m taolib.version
"""
import importlib.metadata
from pathlib import Path
import tomllib
import sys


def get_version(package_name: str = "taolib", fallback: str = "0.0.0") -> str:
    """获取指定包的版本号
    
    首先尝试从已安装的包中获取版本号，如果不可用，则尝试从pyproject.toml中读取。
    
    Args:
        package_name: 要获取版本号的包名
        fallback: 当无法获取版本号时返回的默认值
        
    Returns:
        包的版本号字符串
    """
    # 首先尝试从已安装的包中获取版本号
    version = _get_version_from_installed(package_name)
    if version:
        return version
    
    # 如果未安装，则尝试从pyproject.toml文件中获取
    version = _get_version_from_pyproject(fallback)
    return version


def _get_version_from_pyproject(fallback: str = "0.0.0") -> str:
    """从pyproject.toml文件中获取版本号
    
    Args:
        fallback: 当无法找到或读取pyproject.toml时返回的默认值
        
    Returns:
        从pyproject.toml中读取的版本号或默认值
    """
    # 尝试直接从pyproject.toml读取
    try:
        # 查找项目根目录下的pyproject.toml
        current_dir = Path(__file__).parent
        for parent in [current_dir, *current_dir.parents]:
            pyproject_path = parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    pyproject_data = tomllib.load(f)
                    return pyproject_data.get("project", {}).get("version", fallback)
        return fallback
    except (IOError, tomllib.TOMLDecodeError):
        return fallback


def _get_version_from_installed(package_name: str) -> str | None:
    """从已安装的包元数据中获取版本号
    
    Args:
        package_name: 要获取版本号的包名
        
    Returns:
        包的版本号字符串，如果包未安装则返回None
    """
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


# 获取taolib包的版本号
__version__ = get_version()


def main() -> None:
    """命令行入口函数，用于显示版本号"""
    # 支持显示指定包的版本号
    package_name = "taolib"
    if len(sys.argv) > 1:
        package_name = sys.argv[1]
    
    if package_name == "taolib":
        version = __version__
        print(f"{package_name} version: {version}")
    else:
        version = get_version(package_name, "not found")
        print(f"{package_name} version: {version}")


if __name__ == "__main__":
    main()