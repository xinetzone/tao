"""配置中心客户端 SDK 模块。

提供轻量级客户端，供应用程序获取配置和监听配置变更。
"""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ConfigCenterClient:
    """配置中心客户端。

    提供同步和异步方式获取配置，以及 WebSocket 监听配置变更。
    """

    def __init__(self, base_url: str, token: str, cache_ttl: int = 60) -> None:
        """初始化客户端。

        Args:
            base_url: 配置中心服务器地址
            token: 认证 Token
            cache_ttl: 本地缓存过期时间（秒）
        """
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._cache_ttl = cache_ttl
        self._local_cache: dict[str, tuple[Any, float]] = {}
        self._headers = {"Authorization": f"Bearer {token}"}

    def _cache_key(self, environment: str, service: str, key: str) -> str:
        """生成本地缓存 Key。"""
        return f"{environment}:{service}:{key}"

    def _get_cached(self, key: str) -> Any | None:
        """获取本地缓存。"""
        if key in self._local_cache:
            value, expire_at = self._local_cache[key]
            if time.time() < expire_at:
                return value
            del self._local_cache[key]
        return None

    def _set_cached(self, key: str, value: Any) -> None:
        """设置本地缓存。"""
        self._local_cache[key] = (value, time.time() + self._cache_ttl)

    def get_config(self, key: str, environment: str, service: str) -> Any | None:
        """同步获取配置。

        Args:
            key: 配置键
            environment: 环境类型
            service: 服务名称

        Returns:
            配置值，如果不存在则返回 None
        """
        cache_key = self._cache_key(environment, service, key)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self._base_url}/api/v1/configs",
                    headers=self._headers,
                    params={"environment": environment, "service": service},
                    timeout=10,
                )
                if response.status_code == 200:
                    configs = response.json()
                    for cfg in configs:
                        if cfg["key"] == key:
                            value = cfg["value"]
                            self._set_cached(cache_key, value)
                            return value
                else:
                    logger.warning(
                        f"获取配置失败 (HTTP {response.status_code}): key={key}, environment={environment}, service={service}"
                    )
        except httpx.HTTPError as e:
            logger.warning(
                f"获取配置网络异常: key={key}, environment={environment}, service={service}, error={e}"
            )

        return None

    async def aget_config(self, key: str, environment: str, service: str) -> Any | None:
        """异步获取配置。

        Args:
            key: 配置键
            environment: 环境类型
            service: 服务名称

        Returns:
            配置值，如果不存在则返回 None
        """
        cache_key = self._cache_key(environment, service, key)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/configs",
                    headers=self._headers,
                    params={"environment": environment, "service": service},
                    timeout=10,
                )
                if response.status_code == 200:
                    configs = response.json()
                    for cfg in configs:
                        if cfg["key"] == key:
                            value = cfg["value"]
                            self._set_cached(cache_key, value)
                            return value
                else:
                    logger.warning(
                        f"异步获取配置失败 (HTTP {response.status_code}): key={key}, environment={environment}, service={service}"
                    )
        except httpx.HTTPError as e:
            logger.warning(
                f"异步获取配置网络异常: key={key}, environment={environment}, service={service}, error={e}"
            )

        return None

    def get_configs(self, environment: str, service: str) -> list[dict[str, Any]]:
        """获取服务的所有配置。

        Args:
            environment: 环境类型
            service: 服务名称

        Returns:
            配置列表
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self._base_url}/api/v1/configs",
                    headers=self._headers,
                    params={"environment": environment, "service": service},
                    timeout=10,
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"获取配置列表失败 (HTTP {response.status_code}): environment={environment}, service={service}"
                    )
        except httpx.HTTPError as e:
            logger.warning(
                f"获取配置列表网络异常: environment={environment}, service={service}, error={e}"
            )
        return []

    async def watch_config(
        self,
        key: str,
        environment: str,
        service: str,
        callback: Callable[[dict[str, Any]], None],
    ) -> None:
        """监听配置变更（需要 websockets 依赖）。

        Args:
            key: 配置键
            environment: 环境类型
            service: 服务名称
            callback: 变更回调函数
        """
        try:
            import websockets

            ws_url = self._base_url.replace("http", "ws")
            uri = f"{ws_url}/api/v1/ws/configs?token={self._token}&environments={environment}&services={service}"

            async for websocket in websockets.connect(uri):
                try:
                    async for message in websocket:
                        data = json.loads(message)
                        if data.get("type") == "config_changed":
                            event_data = data.get("data", {})
                            if event_data.get("config_key") == key:
                                # 清除缓存并调用回调
                                cache_key = self._cache_key(environment, service, key)
                                self._local_cache.pop(cache_key, None)
                                callback(event_data)
                except websockets.exceptions.ConnectionClosed:
                    await asyncio.sleep(1)
                    continue
        except ImportError:
            raise RuntimeError(
                "安装 websockets 库以使用 WebSocket 监听功能: pip install websockets"
            )


