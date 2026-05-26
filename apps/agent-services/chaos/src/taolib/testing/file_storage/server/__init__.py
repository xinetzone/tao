"""服务器模块。"""

from taolib.testing.file_storage.server.app import create_app
from taolib.testing.file_storage.server.config import settings

__all__ = [
    "create_app",
    "settings",
]


