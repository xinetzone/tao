#!/usr/bin/env python3
"""测试taolib中的版本模块功能"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parents[1]))

# 导入taolib包并打印版本号
try:
    from src.taolib import __version__, get_version
    print(f"成功导入taolib包")
    print(f"taolib版本号: {__version__}")
    print(f"使用get_version获取taolib版本号: {get_version()}")
    print(f"使用get_version获取其他包版本号(numpy): {get_version('numpy', 'not found')}")
except ImportError as e:
    print(f"导入taolib包失败: {e}")

# 直接从version模块导入版本号
try:
    from src.taolib.version import __version__ as version_module_version
    from src.taolib.version import get_version as version_module_get_version
    print(f"直接从version模块获取版本号: {version_module_version}")
    print(f"使用version模块的get_version获取版本号: {version_module_get_version()}")
except ImportError as e:
    print(f"直接导入version模块失败: {e}")