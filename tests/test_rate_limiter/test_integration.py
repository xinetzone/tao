"""Integration tests for rate limiter with FastAPI."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from taolib.rate_limiter.config import RateLimitConfig
from taolib.rate_limiter.limiter import RateLimiter
from taolib.rate_limiter.middleware import RateLimitMiddleware
from taolib.rate_limiter.models import PathRule, WhitelistConfig
from taolib.rate_limiter.store import InMemoryRateLimitStore


def create_test_app(config: RateLimitConfig) -> FastAPI:
    """创建测试用的 FastAPI 应用。"""
    app = FastAPI()

    store = InMemoryRateLimitStore()
    limiter = RateLimiter(config=config, store=store)

    app.add_middleware(RateLimitMiddleware, limiter=limiter)

    @app.get("/api/test")
    async def test_endpoint():
        return {"message": "ok"}

    @app.get("/api/heavy")
    async def heavy_endpoint():
        return {"message": "heavy computation"}

    @app.get("/health")
    async def health_endpoint():
        return {"status": "healthy"}

    return app


class TestRateLimitIntegration:
    """集成测试：限流中间件与 FastAPI 应用。"""

    def test_default_rate_limit(self):
        """测试默认限流规则生效。"""
        config = RateLimitConfig(default_limit=5, window_seconds=60)
        app = create_test_app(config)
        client = TestClient(app)

        # 发送 5 个请求（应该都成功）
        for i in range(5):
            response = client.get("/api/test")
            assert response.status_code == 200
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers

        # 第 6 个请求应该被限流
        response = client.get("/api/test")
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "rate_limit_exceeded"
        assert "Retry-After" in response.headers
        assert response.headers["X-RateLimit-Remaining"] == "0"

    def test_rate_limit_headers(self):
        """测试限流响应头正确性。"""
        config = RateLimitConfig(default_limit=10, window_seconds=60)
        app = create_test_app(config)
        client = TestClient(app)

        response = client.get("/api/test")
        assert response.status_code == 200
        assert int(response.headers["X-RateLimit-Limit"]) == 10
        assert int(response.headers["X-RateLimit-Remaining"]) == 9
        assert "X-RateLimit-Reset" in response.headers

    def test_429_response_format(self):
        """测试 429 响应格式。"""
        config = RateLimitConfig(default_limit=2, window_seconds=60)
        app = create_test_app(config)
        client = TestClient(app)

        # 超出限流
        client.get("/api/test")
        client.get("/api/test")
        response = client.get("/api/test")

        assert response.status_code == 429
        data = response.json()
        assert "error" in data
        assert "message" in data
        assert "retry_after" in data
        assert "limit" in data
        assert "window_seconds" in data
        assert data["limit"] == 2
        assert data["window_seconds"] == 60


class TestWhitelistIntegration:
    """集成测试：白名单机制。"""

    def test_bypass_paths_not_limited(self):
        """测试 bypass 路径不受限流。"""
        config = RateLimitConfig(
            default_limit=2,
            window_seconds=60,
            whitelist=WhitelistConfig(bypass_paths=["/health"]),
        )
        app = create_test_app(config)
        client = TestClient(app)

        # 发送多个请求到 bypass 路径
        for i in range(10):
            response = client.get("/health")
            assert response.status_code == 200

    def test_same_path_shared_limit(self):
        """测试同一路径共享限流计数器（基于标识符）。"""
        config = RateLimitConfig(default_limit=5, window_seconds=60)
        app = create_test_app(config)
        client = TestClient(app)

        # 同一个路径的请求共享计数器
        for i in range(5):
            response = client.get("/api/test")
            assert response.status_code == 200

        # 第 6 个请求应该被限流
        response = client.get("/api/test")
        assert response.status_code == 429

        # 不同路径有独立的计数器
        response = client.get("/api/heavy")
        assert response.status_code == 200


class TestPathRulesIntegration:
    """集成测试：路径级规则。"""

    def test_path_specific_rules(self):
        """测试路径级限流规则。"""
        config = RateLimitConfig(
            default_limit=100,
            window_seconds=60,
            path_rules={
                "/api/heavy": PathRule(limit=2, window_seconds=60),
            },
        )
        app = create_test_app(config)
        client = TestClient(app)

        # /api/test 使用默认规则（100次）
        for i in range(10):
            response = client.get("/api/test")
            assert response.status_code == 200

        # /api/heavy 使用特定规则（2次）
        client.get("/api/heavy")
        client.get("/api/heavy")
        response = client.get("/api/heavy")
        assert response.status_code == 429


class TestSlidingWindowBehavior:
    """集成测试：滑动窗口行为。"""

    def test_window_expiry_resets_count(self):
        """测试窗口过期后计数重置。"""
        import time

        config = RateLimitConfig(default_limit=3, window_seconds=1)  # 1秒窗口
        app = create_test_app(config)
        client = TestClient(app)

        # 填满限流
        for i in range(3):
            response = client.get("/api/test")
            assert response.status_code == 200

        # 第 4 个请求被限流
        response = client.get("/api/test")
        assert response.status_code == 429

        # 等待窗口过期
        time.sleep(1.1)

        # 请求应该恢复成功
        response = client.get("/api/test")
        assert response.status_code == 200
