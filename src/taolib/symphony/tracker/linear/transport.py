"""Linear 传输层配置工厂 — 创建 HTTPXAsyncTransport 实例。

将传输层配置从客户端逻辑中解耦，方便测试时注入 mock transport。
"""

from gql.transport.httpx import HTTPXAsyncTransport

from taolib.symphony.tracker.models import TrackerConfig

# 默认 User-Agent，标识 Symphony Python 客户端
_USER_AGENT = "Symphony-Python/0.1 (gql+httpx)"


def create_transport(config: TrackerConfig) -> HTTPXAsyncTransport:
    """根据配置创建 :class:`HTTPXAsyncTransport` 实例。

    Args:
        config: Tracker 配置，包含 endpoint、api_key、timeout 等。

    Returns:
        配置好的 :class:`HTTPXAsyncTransport` 实例，可直接注入 :class:`gql.Client`。
    """
    return HTTPXAsyncTransport(
        url=config.endpoint,
        headers={
            "Authorization": config.api_key,
            "Content-Type": "application/json",
            "User-Agent": _USER_AGENT,
        },
        timeout=config.timeout,
    )
