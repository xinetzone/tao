"""Rate Limiter core engine.

Implements the sliding window rate limiting logic with whitelist support
and path-specific rules.
"""
import ipaddress
import time

from .config import RateLimitConfig
from .errors import RateLimitExceededError
from .models import RateLimitResult
from .store import RateLimitStoreProtocol


class RateLimiter:
    """限流引擎核心类。

    负责：
    - 白名单检查
    - 路径规则匹配
    - 滑动窗口计数
    - 限流决策

    Args:
        config: 限流配置
        store: 存储后端（Redis 或内存）
    """

    def __init__(
        self,
        config: RateLimitConfig,
        store: RateLimitStoreProtocol,
    ) -> None:
        self._config = config
        self._store = store

    def is_whitelisted_ip(self, ip: str) -> bool:
        """检查 IP 是否在白名单中。

        Args:
            ip: IP 地址

        Returns:
            是否在白名单中
        """
        whitelist_ips = self._config.whitelist.ips
        if not whitelist_ips:
            return False

        try:
            check_ip = ipaddress.ip_address(ip)
            for whitelist_ip in whitelist_ips:
                # Support CIDR notation
                if "/" in whitelist_ip:
                    if check_ip in ipaddress.ip_network(whitelist_ip, strict=False):
                        return True
                elif check_ip == ipaddress.ip_address(whitelist_ip):
                    return True
        except ValueError:
            pass

        return False

    def is_whitelisted_user(self, user_id: str) -> bool:
        """检查用户 ID 是否在白名单中。

        Args:
            user_id: 用户 ID

        Returns:
            是否在白名单中
        """
        return user_id in self._config.whitelist.user_ids

    def is_bypass_path(self, path: str) -> bool:
        """检查路径是否 bypass 限流。

        Args:
            path: 请求路径

        Returns:
            是否 bypass
        """
        normalized_path = path.rstrip("/").lower()
        bypass_paths = [
            p.rstrip("/").lower() for p in self._config.whitelist.bypass_paths
        ]
        return normalized_path in bypass_paths

    def _get_rule_for_path(self, path: str, method: str) -> tuple[int, int]:
        """获取路径对应的限流规则。

        Args:
            path: 请求路径
            method: HTTP 方法

        Returns:
            (limit, window_seconds) 元组
        """
        normalized_path = path.rstrip("/").lower()

        # Check path-specific rules
        for rule_path, rule in self._config.path_rules.items():
            normalized_rule_path = rule_path.rstrip("/").lower()

            # Check if path matches (exact match or prefix match)
            if normalized_path == normalized_rule_path or normalized_path.startswith(
                normalized_rule_path + "/"
            ):
                # Check method filter
                if rule.methods is not None:
                    if method.upper() not in [m.upper() for m in rule.methods]:
                        continue

                return (
                    rule.limit,
                    rule.window_seconds or self._config.window_seconds,
                )

        # Default rule
        return self._config.default_limit, self._config.window_seconds

    async def check_limit(
        self,
        identifier: str,
        path: str,
        method: str = "GET",
    ) -> RateLimitResult:
        """检查请求是否超出限流阈值。

        Args:
            identifier: 用户标识符（如 "user:abc123" 或 "ip:192.168.1.1"）
            path: 请求路径
            method: HTTP 方法

        Returns:
            限流检查结果

        Raises:
            RateLimitExceededError: 超出限流阈值时
        """
        # Get applicable rule
        limit, window_seconds = self._get_rule_for_path(path, method)

        # Get current request count
        current_count = await self._store.get_request_count(
            identifier, path, method, window_seconds
        )

        # Check if limit exceeded
        remaining = max(0, limit - current_count - 1)

        if current_count >= limit:
            # Calculate retry_after
            oldest = await self._store.get_oldest_in_window(
                identifier, path, method, window_seconds
            )
            if oldest is not None:
                retry_after = int(oldest + window_seconds - time.time()) + 1
                retry_after = max(1, retry_after)
            else:
                retry_after = window_seconds

            raise RateLimitExceededError(
                limit=limit,
                window_seconds=window_seconds,
                retry_after=retry_after,
                identifier=identifier,
            )

        # Request allowed
        now = time.time()
        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=remaining,
            reset_timestamp=now + window_seconds,
        )

    async def record_request(
        self,
        identifier: str,
        path: str,
        method: str = "GET",
    ) -> None:
        """记录请求到存储。

        Args:
            identifier: 用户标识符
            path: 请求路径
            method: HTTP 方法
        """
        now = time.time()
        _, window_seconds = self._get_rule_for_path(path, method)

        await self._store.record_request(identifier, path, method, now, window_seconds)

        # Update stats
        await self._store.increment_stats(identifier, path)


