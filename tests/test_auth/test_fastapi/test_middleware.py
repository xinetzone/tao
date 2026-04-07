"""SimpleAuthMiddleware 集成测试。"""

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

from taolib.auth.api_key import StaticAPIKeyLookup
from taolib.auth.blacklist import InMemoryTokenBlacklist
from taolib.auth.config import AuthConfig
from taolib.auth.fastapi.middleware import SimpleAuthMiddleware
from taolib.auth.models import AuthenticatedUser
from taolib.auth.tokens import JWTService


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(jwt_secret="test-middleware-secret")


@pytest.fixture
def jwt_service(auth_config: AuthConfig) -> JWTService:
    return JWTService(auth_config)


@pytest.fixture
def blacklist() -> InMemoryTokenBlacklist:
    return InMemoryTokenBlacklist()


def _create_app(
    jwt_service: JWTService,
    blacklist: InMemoryTokenBlacklist,
    api_key_lookup: StaticAPIKeyLookup | None = None,
    exclude_paths: list[str] | None = None,
) -> FastAPI:
    """创建带中间件的测试应用。"""
    app = FastAPI()

    app.add_middleware(
        SimpleAuthMiddleware,
        jwt_service=jwt_service,
        blacklist=blacklist,
        api_key_lookup=api_key_lookup,
        exclude_paths=exclude_paths or ["/public", "/docs", "/health"],
    )

    @app.get("/protected")
    async def protected(request: Request):
        user = request.state.user
        return {"user_id": user.user_id, "roles": user.roles}

    @app.get("/public")
    async def public(request: Request):
        return {"user": getattr(request.state, "user", None)}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


class TestSimpleAuthMiddleware:
    """测试 SimpleAuthMiddleware。"""

    @pytest.mark.asyncio
    async def test_valid_jwt(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试有效 JWT 通过中间件。"""
        app = _create_app(jwt_service, blacklist)
        token = jwt_service.create_access_token("user-1", ["admin"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        assert resp.json()["user_id"] == "user-1"

    @pytest.mark.asyncio
    async def test_no_auth_returns_401(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试无凭据返回 401。"""
        app = _create_app(jwt_service, blacklist)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get("/protected")

        assert resp.status_code == 401
        assert "未提供认证凭据" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_expired_jwt_returns_401(self, blacklist: InMemoryTokenBlacklist):
        """测试过期 JWT 返回 401。"""
        from datetime import timedelta

        config = AuthConfig(
            jwt_secret="test-secret", access_token_ttl=timedelta(seconds=-1)
        )
        service = JWTService(config)
        app = _create_app(service, blacklist)
        token = service.create_access_token("user-1", ["admin"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 401
        assert "过期" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_blacklisted_jwt(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试黑名单 JWT 返回 401。"""
        app = _create_app(jwt_service, blacklist)
        token = jwt_service.create_access_token("user-1", ["admin"])

        payload = jwt_service.verify_access_token(token)
        await blacklist.add(payload.jti, ttl_seconds=3600)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 401
        assert "吊销" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_excluded_path_skips_auth(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试排除路径跳过认证。"""
        app = _create_app(jwt_service, blacklist)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get("/public")

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_endpoint(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试健康检查端点跳过认证。"""
        app = _create_app(jwt_service, blacklist)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get("/health")

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_api_key_via_header(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试 X-API-Key 头部认证。"""
        api_keys = StaticAPIKeyLookup(
            {
                "my-api-key": AuthenticatedUser(
                    user_id="bot",
                    roles=["viewer"],
                    auth_method="api_key",
                ),
            },
        )
        app = _create_app(jwt_service, blacklist, api_key_lookup=api_keys)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"X-API-Key": "my-api-key"},
            )

        assert resp.status_code == 200
        assert resp.json()["user_id"] == "bot"

    @pytest.mark.asyncio
    async def test_api_key_via_auth_header(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试 Authorization: ApiKey 头部认证。"""
        api_keys = StaticAPIKeyLookup(
            {
                "my-api-key": AuthenticatedUser(
                    user_id="bot",
                    roles=["viewer"],
                    auth_method="api_key",
                ),
            },
        )
        app = _create_app(jwt_service, blacklist, api_key_lookup=api_keys)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"Authorization": "ApiKey my-api-key"},
            )

        assert resp.status_code == 200
        assert resp.json()["user_id"] == "bot"

    @pytest.mark.asyncio
    async def test_invalid_api_key(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试无效 API 密钥返回 401。"""
        api_keys = StaticAPIKeyLookup(
            {
                "valid-key": AuthenticatedUser(
                    user_id="bot",
                    roles=["viewer"],
                    auth_method="api_key",
                ),
            },
        )
        app = _create_app(jwt_service, blacklist, api_key_lookup=api_keys)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"X-API-Key": "wrong-key"},
            )

        assert resp.status_code == 401
