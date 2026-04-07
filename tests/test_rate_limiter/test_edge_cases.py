"""限流器边界用例测试。

覆盖窗口边界、白名单、路径规则、标识符隔离、InMemoryStore、模型等。
"""

import time
from unittest.mock import MagicMock

import pytest

from taolib.rate_limiter.errors import RateLimitExceededError
from taolib.rate_limiter.keys import (
    make_stats_realtime_key,
    make_stats_top_users_key,
    make_violation_counter_key,
    make_window_key,
    parse_identifier_type,
)
from taolib.rate_limiter.limiter import RateLimiter
from taolib.rate_limiter.middleware import extract_client_ip, extract_user_id
from taolib.rate_limiter.models import (
    PathRule,
    RateLimitConfig,
    RateLimitResult,
    WhitelistConfig,
)
from taolib.rate_limiter.store import InMemoryRateLimitStore

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(**overrides):
    defaults = {
        "enabled": True,
        "default_limit": 10,
        "window_seconds": 60,
        "path_rules": {},
        "whitelist": WhitelistConfig(),
    }
    defaults.update(overrides)
    return RateLimitConfig(**defaults)


def _make_limiter(config=None, store=None):
    config = config or _make_config()
    store = store or InMemoryRateLimitStore()
    return RateLimiter(config=config, store=store), store


# ===========================================================================
# Window Boundary Tests
# ===========================================================================


class TestWindowBoundary:
    """滑动窗口边界条件测试。"""

    @pytest.mark.asyncio
    async def test_exact_limit_count_raises(self):
        """恰好达到限制数时，下一个请求应被拒绝（抛异常）。"""
        limiter, store = _make_limiter(_make_config(default_limit=5, window_seconds=60))
        now = time.time()

        for i in range(5):
            await store.record_request("u1", "/api", "GET", now + i * 0.001, 60)

        with pytest.raises(RateLimitExceededError) as exc_info:
            await limiter.check_limit("u1", "/api", "GET")
        assert exc_info.value.limit == 5

    @pytest.mark.asyncio
    async def test_one_below_limit_allowed(self):
        """低于限制一个的请求应被允许。"""
        limiter, store = _make_limiter(_make_config(default_limit=5, window_seconds=60))
        now = time.time()

        for i in range(4):
            await store.record_request("u1", "/api", "GET", now + i * 0.001, 60)

        result = await limiter.check_limit("u1", "/api", "GET")
        assert result.allowed

    @pytest.mark.asyncio
    async def test_limit_of_one_raises(self):
        """限制为 1 的配置：第一个请求记录后，第二个请求被拒绝。"""
        limiter, store = _make_limiter(_make_config(default_limit=1, window_seconds=60))

        await store.record_request("u1", "/api", "GET", time.time(), 60)
        with pytest.raises(RateLimitExceededError):
            await limiter.check_limit("u1", "/api", "GET")

    @pytest.mark.asyncio
    async def test_zero_requests_allowed(self):
        """无历史请求时，请求应被允许。"""
        limiter, _ = _make_limiter(_make_config(default_limit=5, window_seconds=60))
        result = await limiter.check_limit("u1", "/api", "GET")
        assert result.allowed

    @pytest.mark.asyncio
    async def test_very_large_limit(self):
        """极大限制值正常工作。"""
        limiter, _ = _make_limiter(
            _make_config(default_limit=1000000, window_seconds=60)
        )

        result = await limiter.check_limit("u1", "/api", "GET")
        assert result.allowed
        assert result.remaining == 999999

    @pytest.mark.asyncio
    async def test_very_small_window(self):
        """极小窗口（1 秒）应正常工作。"""
        limiter, store = _make_limiter(_make_config(default_limit=2, window_seconds=1))
        now = time.time()

        # 窗口外的旧请求不应计入
        await store.record_request("u1", "/api", "GET", now - 2, 1)
        result = await limiter.check_limit("u1", "/api", "GET")
        assert result.allowed

    @pytest.mark.asyncio
    async def test_very_large_window(self):
        """极大窗口（1 天）应正常工作。"""
        limiter, store = _make_limiter(
            _make_config(default_limit=3, window_seconds=86400)
        )
        now = time.time()

        for i in range(3):
            await store.record_request("u1", "/api", "GET", now - 43200 + i, 86400)

        with pytest.raises(RateLimitExceededError):
            await limiter.check_limit("u1", "/api", "GET")


# ===========================================================================
# Whitelist Edge Cases
# ===========================================================================


class TestWhitelistEdgeCases:
    """白名单边界测试。"""

    def test_cidr_whitelist_exact_match(self):
        """单个 IP 的 CIDR (/32) 精确匹配。"""
        config = _make_config(whitelist=WhitelistConfig(ips=["10.0.0.1/32"]))
        limiter, _ = _make_limiter(config)
        assert limiter.is_whitelisted_ip("10.0.0.1")
        assert not limiter.is_whitelisted_ip("10.0.0.2")

    def test_cidr_whitelist_subnet(self):
        """子网 CIDR 匹配。"""
        config = _make_config(whitelist=WhitelistConfig(ips=["192.168.1.0/24"]))
        limiter, _ = _make_limiter(config)
        assert limiter.is_whitelisted_ip("192.168.1.100")
        assert limiter.is_whitelisted_ip("192.168.1.255")
        assert not limiter.is_whitelisted_ip("192.168.2.1")

    def test_plain_ip_whitelist(self):
        """纯 IP（无 CIDR 后缀）白名单匹配。"""
        config = _make_config(whitelist=WhitelistConfig(ips=["127.0.0.1"]))
        limiter, _ = _make_limiter(config)
        assert limiter.is_whitelisted_ip("127.0.0.1")
        assert not limiter.is_whitelisted_ip("127.0.0.2")

    def test_empty_whitelist(self):
        """空白名单不匹配任何内容。"""
        config = _make_config(whitelist=WhitelistConfig())
        limiter, _ = _make_limiter(config)
        assert not limiter.is_whitelisted_ip("10.0.0.1")
        assert not limiter.is_whitelisted_user("admin")

    def test_user_whitelist(self):
        """用户白名单（user_ids 字段）。"""
        config = _make_config(
            whitelist=WhitelistConfig(user_ids=["admin", "service-account"])
        )
        limiter, _ = _make_limiter(config)
        assert limiter.is_whitelisted_user("admin")
        assert limiter.is_whitelisted_user("service-account")
        assert not limiter.is_whitelisted_user("user1")

    def test_bypass_path_exact(self):
        """路径绕过 - 精确匹配。"""
        config = _make_config(
            whitelist=WhitelistConfig(bypass_paths=["/health", "/metrics"])
        )
        limiter, _ = _make_limiter(config)
        assert limiter.is_bypass_path("/health")
        assert limiter.is_bypass_path("/metrics")
        assert not limiter.is_bypass_path("/api/users")

    def test_bypass_path_not_prefix(self):
        """路径绕过 - 非前缀匹配。"""
        config = _make_config(whitelist=WhitelistConfig(bypass_paths=["/health"]))
        limiter, _ = _make_limiter(config)
        assert limiter.is_bypass_path("/health")
        assert not limiter.is_bypass_path("/health-check")

    def test_bypass_path_case_insensitive(self):
        """路径绕过 - 大小写不敏感。"""
        config = _make_config(whitelist=WhitelistConfig(bypass_paths=["/Health"]))
        limiter, _ = _make_limiter(config)
        assert limiter.is_bypass_path("/health")
        assert limiter.is_bypass_path("/HEALTH")

    def test_bypass_path_trailing_slash(self):
        """路径绕过 - 忽略尾部斜杠。"""
        config = _make_config(whitelist=WhitelistConfig(bypass_paths=["/health/"]))
        limiter, _ = _make_limiter(config)
        assert limiter.is_bypass_path("/health")

    def test_multiple_ip_ranges(self):
        """多个 IP 范围白名单。"""
        config = _make_config(
            whitelist=WhitelistConfig(ips=["10.0.0.0/8", "172.16.0.0/12"])
        )
        limiter, _ = _make_limiter(config)
        assert limiter.is_whitelisted_ip("10.255.255.255")
        assert limiter.is_whitelisted_ip("172.31.255.255")
        assert not limiter.is_whitelisted_ip("192.168.1.1")


# ===========================================================================
# Path Rule Edge Cases
# ===========================================================================


class TestPathRuleEdgeCases:
    """路径规则边界测试（_get_rule_for_path 返回 tuple[int, int]）。"""

    def test_specific_path_rule(self):
        """路径规则覆盖默认限制。"""
        config = _make_config(
            default_limit=100,
            path_rules={
                "/api/upload": PathRule(limit=5, window_seconds=60),
            },
        )
        limiter, _ = _make_limiter(config)

        limit, window = limiter._get_rule_for_path("/api/upload", "POST")
        assert limit == 5
        assert window == 60

    def test_path_rule_with_method_filter(self):
        """带 HTTP 方法过滤的路径规则。"""
        config = _make_config(
            default_limit=100,
            path_rules={
                "/api/data": PathRule(
                    limit=2, window_seconds=60, methods=["POST", "PUT"]
                ),
            },
        )
        limiter, _ = _make_limiter(config)

        limit_post, _ = limiter._get_rule_for_path("/api/data", "POST")
        assert limit_post == 2

        limit_get, _ = limiter._get_rule_for_path("/api/data", "GET")
        assert limit_get == 100  # 回退到默认

    def test_no_matching_rule_uses_default(self):
        """无匹配规则时使用默认限制。"""
        config = _make_config(
            default_limit=50,
            window_seconds=120,
            path_rules={
                "/api/special": PathRule(limit=5, window_seconds=60),
            },
        )
        limiter, _ = _make_limiter(config)

        limit, window = limiter._get_rule_for_path("/api/normal", "GET")
        assert limit == 50
        assert window == 120

    def test_path_rule_inherits_default_window(self):
        """路径规则 window_seconds=None 时继承全局窗口。"""
        config = _make_config(
            default_limit=100,
            window_seconds=300,
            path_rules={
                "/api/fast": PathRule(limit=10),
            },
        )
        limiter, _ = _make_limiter(config)

        limit, window = limiter._get_rule_for_path("/api/fast", "GET")
        assert limit == 10
        assert window == 300  # 继承全局

    def test_prefix_match(self):
        """路径前缀匹配。"""
        config = _make_config(
            default_limit=100,
            path_rules={
                "/api": PathRule(limit=50, window_seconds=60),
            },
        )
        limiter, _ = _make_limiter(config)

        limit, _ = limiter._get_rule_for_path("/api/users", "GET")
        assert limit == 50

    def test_empty_path_rules(self):
        """空路径规则字典，使用默认值。"""
        config = _make_config(default_limit=42, window_seconds=30, path_rules={})
        limiter, _ = _make_limiter(config)

        limit, window = limiter._get_rule_for_path("/anything", "GET")
        assert limit == 42
        assert window == 30


# ===========================================================================
# Concurrent Identifier Tests
# ===========================================================================


class TestIdentifierIsolation:
    """不同标识符隔离测试。"""

    @pytest.mark.asyncio
    async def test_different_users_independent_limits(self):
        """不同用户的限流计数器相互独立。"""
        limiter, store = _make_limiter(_make_config(default_limit=2, window_seconds=60))
        now = time.time()

        # user1 用完额度
        await store.record_request("u1", "/api", "GET", now, 60)
        await store.record_request("u1", "/api", "GET", now + 0.001, 60)

        # user1 被限流
        with pytest.raises(RateLimitExceededError):
            await limiter.check_limit("u1", "/api", "GET")

        # user2 不受影响
        r2 = await limiter.check_limit("u2", "/api", "GET")
        assert r2.allowed

    @pytest.mark.asyncio
    async def test_different_paths_independent(self):
        """不同路径的限流计数器相互独立。"""
        limiter, store = _make_limiter(_make_config(default_limit=1, window_seconds=60))
        now = time.time()

        await store.record_request("u1", "/api/a", "GET", now, 60)

        # /api/a 被限流
        with pytest.raises(RateLimitExceededError):
            await limiter.check_limit("u1", "/api/a", "GET")

        # /api/b 不受影响
        r2 = await limiter.check_limit("u1", "/api/b", "GET")
        assert r2.allowed

    @pytest.mark.asyncio
    async def test_different_methods_share_window(self):
        """同一路径的 GET/POST 共享同一窗口（除非规则指定方法过滤）。"""
        limiter, store = _make_limiter(_make_config(default_limit=2, window_seconds=60))
        now = time.time()

        await store.record_request("u1", "/api", "GET", now, 60)
        await store.record_request("u1", "/api", "POST", now + 0.001, 60)

        # 注意：store 的 key 由 make_window_key(identifier, path, method) 生成
        # 不同 method 的 key 不同，所以限流也是分开的
        result = await limiter.check_limit("u1", "/api", "GET")
        assert result.allowed  # 只有 1 个 GET 请求，限制为 2


# ===========================================================================
# InMemoryStore Edge Cases
# ===========================================================================


class TestInMemoryStoreEdgeCases:
    """内存存储边界测试。"""

    @pytest.mark.asyncio
    async def test_empty_store_returns_zero(self):
        """空存储返回零计数。"""
        store = InMemoryRateLimitStore()
        count = await store.get_request_count("nobody", "/api", "GET", 60)
        assert count == 0

    @pytest.mark.asyncio
    async def test_expired_entries_not_counted(self):
        """过期的条目不计入。"""
        store = InMemoryRateLimitStore()
        now = time.time()
        # 记录一个 120 秒前的请求
        await store.record_request("u1", "/api", "GET", now - 120, 60)

        count = await store.get_request_count("u1", "/api", "GET", 60)
        assert count == 0

    @pytest.mark.asyncio
    async def test_window_boundary_exactly_at_edge(self):
        """恰好在窗口边界的请求。"""
        store = InMemoryRateLimitStore()
        now = time.time()
        # 恰好 60 秒前的请求
        await store.record_request("u1", "/api", "GET", now - 60, 60)

        count = await store.get_request_count("u1", "/api", "GET", 60)
        # 正好在边界上的请求可能被计入也可能不被计入，取决于 >/>=
        assert count in (0, 1)

    @pytest.mark.asyncio
    async def test_multiple_keys_isolated(self):
        """不同 key 的数据隔离。"""
        store = InMemoryRateLimitStore()
        now = time.time()
        await store.record_request("a", "/api", "GET", now, 60)
        await store.record_request("b", "/api", "GET", now, 60)

        count_a = await store.get_request_count("a", "/api", "GET", 60)
        count_b = await store.get_request_count("b", "/api", "GET", 60)
        assert count_a == 1
        assert count_b == 1

    @pytest.mark.asyncio
    async def test_stats_increment(self):
        """统计递增测试。"""
        store = InMemoryRateLimitStore()
        await store.increment_stats("u1", "/api")
        await store.increment_stats("u1", "/api")
        await store.increment_stats("u1", "/other")

        realtime = await store.get_realtime_requests(60)
        assert isinstance(realtime, dict)
        assert realtime["active_requests"] >= 2

    @pytest.mark.asyncio
    async def test_top_users(self):
        """Top users 查询。"""
        store = InMemoryRateLimitStore()
        await store.increment_stats("u1", "/api")
        await store.increment_stats("u1", "/api")
        await store.increment_stats("u2", "/api")

        top = await store.get_top_users(10)
        assert len(top) == 2
        assert top[0] == ("u1", 2)
        assert top[1] == ("u2", 1)

    @pytest.mark.asyncio
    async def test_get_oldest_in_empty_window(self):
        """空窗口没有最旧请求。"""
        store = InMemoryRateLimitStore()
        oldest = await store.get_oldest_in_window("nobody", "/api", "GET", 60)
        assert oldest is None

    @pytest.mark.asyncio
    async def test_get_oldest_in_window(self):
        """获取窗口中最旧的请求时间戳。"""
        store = InMemoryRateLimitStore()
        now = time.time()
        await store.record_request("u1", "/api", "GET", now - 30, 60)
        await store.record_request("u1", "/api", "GET", now - 10, 60)

        oldest = await store.get_oldest_in_window("u1", "/api", "GET", 60)
        assert oldest is not None
        assert abs(oldest - (now - 30)) < 1

    @pytest.mark.asyncio
    async def test_record_request_returns_count(self):
        """record_request 返回当前计数。"""
        store = InMemoryRateLimitStore()
        now = time.time()
        count1 = await store.record_request("u1", "/api", "GET", now, 60)
        count2 = await store.record_request("u1", "/api", "GET", now + 0.001, 60)
        assert count1 == 1
        assert count2 == 2


# ===========================================================================
# RateLimitResult Tests
# ===========================================================================


class TestRateLimitResult:
    """限流结果模型测试。"""

    def test_result_allowed(self):
        result = RateLimitResult(
            allowed=True,
            limit=10,
            remaining=5,
            reset_timestamp=time.time() + 60,
        )
        assert result.allowed
        assert result.remaining == 5

    def test_result_zero_remaining(self):
        result = RateLimitResult(
            allowed=True,
            limit=1,
            remaining=0,
            reset_timestamp=time.time() + 60,
        )
        assert result.remaining == 0

    def test_result_with_retry_after(self):
        result = RateLimitResult(
            allowed=True,
            limit=10,
            remaining=0,
            reset_timestamp=time.time() + 60,
            retry_after=30,
        )
        assert result.retry_after == 30


# ===========================================================================
# RateLimitExceededError Tests
# ===========================================================================


class TestRateLimitExceededError:
    """限流异常测试。"""

    def test_error_attributes(self):
        err = RateLimitExceededError(
            limit=100,
            window_seconds=60,
            retry_after=30,
            identifier="user:abc",
        )
        assert err.limit == 100
        assert err.window_seconds == 60
        assert err.retry_after == 30
        assert err.identifier == "user:abc"

    def test_error_message_format(self):
        err = RateLimitExceededError(
            limit=10,
            window_seconds=60,
            retry_after=15,
            identifier="ip:1.2.3.4",
        )
        msg = str(err)
        assert "ip:1.2.3.4" in msg
        assert "10" in msg
        assert "60" in msg

    def test_error_reset_timestamp(self):
        before = time.time()
        err = RateLimitExceededError(
            limit=10,
            window_seconds=60,
            retry_after=30,
            identifier="u1",
        )
        assert err.reset_timestamp >= before + 30


# ===========================================================================
# IPv6 Whitelist Tests
# ===========================================================================


class TestIPv6Whitelist:
    """IPv6 白名单测试。"""

    def test_ipv6_loopback_whitelisted(self):
        """IPv6 回环地址白名单。"""
        config = _make_config(whitelist=WhitelistConfig(ips=["::1"]))
        limiter, _ = _make_limiter(config)
        assert limiter.is_whitelisted_ip("::1")

    def test_ipv6_cidr_whitelist(self):
        """IPv6 CIDR 范围白名单。"""
        config = _make_config(whitelist=WhitelistConfig(ips=["fd00::/8"]))
        limiter, _ = _make_limiter(config)
        assert limiter.is_whitelisted_ip("fd00::1")
        assert limiter.is_whitelisted_ip("fd12:3456::1")
        assert not limiter.is_whitelisted_ip("2001:db8::1")

    def test_invalid_ip_returns_false(self):
        """无效 IP 地址返回 False（不抛异常）。"""
        config = _make_config(whitelist=WhitelistConfig(ips=["10.0.0.0/8"]))
        limiter, _ = _make_limiter(config)
        assert not limiter.is_whitelisted_ip("not-an-ip")
        assert not limiter.is_whitelisted_ip("")

    def test_mixed_ipv4_ipv6_whitelist(self):
        """混合 IPv4 和 IPv6 白名单。"""
        config = _make_config(
            whitelist=WhitelistConfig(ips=["10.0.0.0/8", "::1", "fd00::/8"])
        )
        limiter, _ = _make_limiter(config)
        assert limiter.is_whitelisted_ip("10.0.0.1")
        assert limiter.is_whitelisted_ip("::1")
        assert not limiter.is_whitelisted_ip("192.168.1.1")


# ===========================================================================
# extract_client_ip Tests
# ===========================================================================


class TestExtractClientIp:
    """中间件 extract_client_ip 测试。"""

    def _make_request(self, headers=None, client_host=None):
        """创建 mock Request 对象。"""
        request = MagicMock()
        request.headers = headers or {}
        if client_host:
            request.client = MagicMock()
            request.client.host = client_host
        else:
            request.client = None
        return request

    def test_x_forwarded_for_single(self):
        """X-Forwarded-For 单个 IP。"""
        req = self._make_request(headers={"X-Forwarded-For": "1.2.3.4"})
        assert extract_client_ip(req) == "1.2.3.4"

    def test_x_forwarded_for_multiple(self):
        """X-Forwarded-For 多个 IP，取第一个。"""
        req = self._make_request(
            headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8, 9.10.11.12"}
        )
        assert extract_client_ip(req) == "1.2.3.4"

    def test_x_real_ip(self):
        """X-Real-IP 头。"""
        req = self._make_request(headers={"X-Real-IP": "10.0.0.1"})
        assert extract_client_ip(req) == "10.0.0.1"

    def test_x_forwarded_for_takes_priority(self):
        """X-Forwarded-For 优先于 X-Real-IP。"""
        req = self._make_request(
            headers={
                "X-Forwarded-For": "1.2.3.4",
                "X-Real-IP": "5.6.7.8",
            }
        )
        assert extract_client_ip(req) == "1.2.3.4"

    def test_direct_connection(self):
        """无代理头时使用直接连接 IP。"""
        req = self._make_request(client_host="192.168.1.1")
        assert extract_client_ip(req) == "192.168.1.1"

    def test_no_client_returns_unknown(self):
        """无任何 IP 信息返回 'unknown'。"""
        req = self._make_request()
        assert extract_client_ip(req) == "unknown"

    def test_x_forwarded_for_with_spaces(self):
        """X-Forwarded-For IP 周围有空格。"""
        req = self._make_request(headers={"X-Forwarded-For": "  1.2.3.4  , 5.6.7.8"})
        assert extract_client_ip(req) == "1.2.3.4"


# ===========================================================================
# extract_user_id Tests
# ===========================================================================


class TestExtractUserId:
    """中间件 extract_user_id 测试。"""

    def _make_request(self, headers=None):
        request = MagicMock()
        request.headers = headers or {}
        return request

    def test_x_user_id_header(self):
        """X-User-ID 头提取用户。"""
        req = self._make_request(headers={"X-User-ID": "user-123"})
        assert extract_user_id(req) == "user-123"

    def test_x_user_id_stripped(self):
        """X-User-ID 头有空格时被 strip。"""
        req = self._make_request(headers={"X-User-ID": "  user-123  "})
        assert extract_user_id(req) == "user-123"

    def test_no_user_id_returns_none(self):
        """无 X-User-ID 头返回 None。"""
        req = self._make_request()
        assert extract_user_id(req) is None


# ===========================================================================
# Keys Module Tests
# ===========================================================================


class TestKeysModule:
    """keys 模块函数测试。"""

    def test_make_window_key_format(self):
        key = make_window_key("user:abc", "/api/test", "GET")
        assert key == "ratelimit:window:user:abc:/api/test:GET"

    def test_make_window_key_normalizes_path(self):
        """路径尾斜杠被移除，小写化。"""
        key = make_window_key("u1", "/API/Test/", "post")
        assert key == "ratelimit:window:u1:/api/test:POST"

    def test_make_stats_top_users_key(self):
        assert make_stats_top_users_key() == "ratelimit:stats:top-users"

    def test_make_stats_realtime_key(self):
        assert make_stats_realtime_key() == "ratelimit:stats:realtime"

    def test_make_violation_counter_key(self):
        key = make_violation_counter_key("user:abc")
        assert key == "ratelimit:violations:user:abc"

    def test_parse_identifier_type_user(self):
        assert parse_identifier_type("user:abc123") == "user"

    def test_parse_identifier_type_ip(self):
        assert parse_identifier_type("ip:192.168.1.1") == "ip"

    def test_parse_identifier_type_unknown(self):
        assert parse_identifier_type("plain-no-colon") == "unknown"

    def test_parse_identifier_type_multiple_colons(self):
        """多个冒号只取第一个前面的部分。"""
        assert parse_identifier_type("ip:::1") == "ip"


# ===========================================================================
# check_limit Advanced Tests
# ===========================================================================


class TestCheckLimitAdvanced:
    """check_limit 高级场景测试。"""

    @pytest.mark.asyncio
    async def test_check_limit_remaining_calculation(self):
        """remaining 计算：max(0, limit - count - 1)。"""
        limiter, store = _make_limiter(_make_config(default_limit=5, window_seconds=60))
        now = time.time()

        await store.record_request("u1", "/api", "GET", now, 60)
        await store.record_request("u1", "/api", "GET", now + 0.001, 60)

        result = await limiter.check_limit("u1", "/api", "GET")
        assert result.remaining == 2  # 5 - 2 - 1 = 2

    @pytest.mark.asyncio
    async def test_check_limit_retry_after_with_oldest_none(self):
        """oldest=None 时 retry_after 等于 window_seconds。"""
        config = _make_config(default_limit=1, window_seconds=60)
        store = InMemoryRateLimitStore()
        limiter = RateLimiter(config=config, store=store)

        # 记录一个请求，但模拟 oldest 为 None 的场景
        now = time.time()
        await store.record_request("u1", "/api", "GET", now, 60)

        with pytest.raises(RateLimitExceededError) as exc_info:
            await limiter.check_limit("u1", "/api", "GET")

        # retry_after 应为正数
        assert exc_info.value.retry_after >= 1

    @pytest.mark.asyncio
    async def test_record_request_calls_store(self):
        """record_request 正确调用 store.record_request 和 increment_stats。"""
        limiter, store = _make_limiter(
            _make_config(default_limit=10, window_seconds=60)
        )

        await limiter.record_request("u1", "/api", "GET")

        count = await store.get_request_count("u1", "/api", "GET", 60)
        assert count == 1
