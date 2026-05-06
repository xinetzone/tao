"""Symphony HTTP 服务器子包。

提供 REST JSON API 和 HTML 仪表板，用于监控编排状态。
"""

from .app import create_app

__all__ = ["create_app"]
