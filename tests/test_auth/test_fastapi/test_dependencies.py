"""FastAPI 依赖注入和中间件集成测试。"""

from datetime import timedelta

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from taolib.auth.api_key import StaticAPIKeyLookup
from taolib.auth.blacklist import InMemoryTokenBlacklist
from taolib.auth.config import AuthConfig
from taolib.auth.fastapi.dependencies import (
    create_auth_dependency,
    require_permissions,
    require_roles,
    require_scope,
)
from taolib.auth.models import AuthenticatedUser
from taolib.auth.rbac import Permission, RBACPolicy, RoleDefinition
from taolib.auth.tokens import JWTService


@pytest.fixture
def auth_config() -> AuthConfig:
    return AuthConfig(jwt_secret="test-fastapi-secret")


@pytest.fixture
def jwt_service(auth_config: AuthConfig) -> JWTService:
    return JWTService(auth_config)


@pytest.fixture
def blacklist() -> InMemoryTokenBlacklist:
    return InMemoryTokenBlacklist()


@pytest.fixture
def api_key_lookup() -> StaticAPIKeyLookup:
    return StaticAPIKeyLookup(
        {
            "valid-api-key-123": AuthenticatedUser(
                user_id="bot-user",
                roles=["config_viewer"],
                auth_method="api_key",
                metadata={"key_name": "test-key"},
            ),
        },
    )


@pytest.fixture
def rbac_policy() -> RBACPolicy:
    return RBACPolicy(
        roles={
            "admin": RoleDefinition(
                name="admin",
                description="管理员",
                permissions=[
                    Permission(resource="config", action="read"),
                    Permission(resource="config", action="write"),
                ],
                scopes={"environment": None},
            ),
            "config_viewer": RoleDefinition(
                name="config_viewer",
                description="查看者",
                permissions=[Permission(resource="config", action="read")],
                scopes={"environment": ["development"]},
            ),
        },
    )


def _create_app(
    jwt_service: JWTService,
    blacklist: InMemoryTokenBlacklist,
    api_key_lookup: StaticAPIKeyLookup | None = None,
    rbac_policy: RBACPolicy | None = None,
) -> FastAPI:
    """创建测试用 FastAPI 应用。"""
    app = FastAPI()

    auth = create_auth_dependency(
        jwt_service=jwt_service,
        blacklist=blacklist,
        api_key_lookup=api_key_lookup,
    )

    @app.get("/protected")
    async def protected(user: AuthenticatedUser = Depends(auth)):
        return {
            "user_id": user.user_id,
            "roles": user.roles,
            "method": user.auth_method,
        }

    @app.get("/public")
    async def public():
        return {"status": "ok"}

    if rbac_policy:
        admin_dep = require_roles("admin", auth_dependency=auth)

        @app.get("/admin-only")
        async def admin_only(user: AuthenticatedUser = Depends(admin_dep)):
            return {"user_id": user.user_id}

        perm_dep = require_permissions(
            "config", "write", rbac_policy, auth_dependency=auth
        )

        @app.get("/write-config")
        async def write_config(user: AuthenticatedUser = Depends(perm_dep)):
            return {"user_id": user.user_id}

        scope_dep = require_scope(
            "environment", "production", rbac_policy, auth_dependency=auth
        )

        @app.get("/prod-access")
        async def prod_access(user: AuthenticatedUser = Depends(scope_dep)):
            return {"user_id": user.user_id}

    return app


class TestJWTAuthentication:
    """测试 JWT 认证。"""

    @pytest.mark.asyncio
    async def test_valid_jwt(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试有效 JWT 认证。"""
        app = _create_app(jwt_service, blacklist)
        token = jwt_service.create_access_token("user-123", ["admin"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == "user-123"
        assert data["roles"] == ["admin"]
        assert data["method"] == "jwt"

    @pytest.mark.asyncio
    async def test_no_credentials(
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
    async def test_expired_jwt(self, blacklist: InMemoryTokenBlacklist):
        """测试过期 JWT 返回 401。"""
        config = AuthConfig(
            jwt_secret="test-secret", access_token_ttl=timedelta(seconds=-1)
        )
        service = JWTService(config)
        app = _create_app(service, blacklist)
        token = service.create_access_token("user-123", ["admin"])

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
    async def test_invalid_jwt(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试无效 JWT 返回 401。"""
        app = _create_app(jwt_service, blacklist)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"Authorization": "Bearer invalid-token"},
            )

        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_blacklisted_jwt(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试黑名单中的 JWT 返回 401。"""
        app = _create_app(jwt_service, blacklist)
        token = jwt_service.create_access_token("user-123", ["admin"])

        # 获取 jti 并加入黑名单
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
    async def test_public_endpoint(
        self, jwt_service: JWTService, blacklist: InMemoryTokenBlacklist
    ):
        """测试公开端点不需要认证。"""
        app = _create_app(jwt_service, blacklist)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get("/public")

        assert resp.status_code == 200


class TestAPIKeyAuthentication:
    """测试 API 密钥认证。"""

    @pytest.mark.asyncio
    async def test_valid_api_key_header(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        api_key_lookup: StaticAPIKeyLookup,
    ):
        """测试有效 X-API-Key 头部。"""
        app = _create_app(jwt_service, blacklist, api_key_lookup)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"X-API-Key": "valid-api-key-123"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == "bot-user"
        assert data["method"] == "api_key"

    @pytest.mark.asyncio
    async def test_invalid_api_key(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        api_key_lookup: StaticAPIKeyLookup,
    ):
        """测试无效 API 密钥返回 401。"""
        app = _create_app(jwt_service, blacklist, api_key_lookup)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={"X-API-Key": "invalid-key"},
            )

        assert resp.status_code == 401
        assert "API 密钥" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_jwt_takes_priority_over_api_key(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        api_key_lookup: StaticAPIKeyLookup,
    ):
        """测试 JWT 优先于 API Key。"""
        app = _create_app(jwt_service, blacklist, api_key_lookup)
        token = jwt_service.create_access_token("jwt-user", ["admin"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/protected",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-API-Key": "valid-api-key-123",
                },
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == "jwt-user"
        assert data["method"] == "jwt"


class TestRoleBasedAccess:
    """测试基于角色的访问控制。"""

    @pytest.mark.asyncio
    async def test_admin_role_access(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        rbac_policy: RBACPolicy,
    ):
        """测试管理员角色可以访问。"""
        app = _create_app(jwt_service, blacklist, rbac_policy=rbac_policy)
        token = jwt_service.create_access_token("admin-user", ["admin"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/admin-only",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_non_admin_role_denied(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        rbac_policy: RBACPolicy,
    ):
        """测试非管理员角色被拒绝。"""
        app = _create_app(jwt_service, blacklist, rbac_policy=rbac_policy)
        token = jwt_service.create_access_token("viewer-user", ["config_viewer"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/admin-only",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 403
        assert "权限不足" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_permission_check_allowed(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        rbac_policy: RBACPolicy,
    ):
        """测试有写权限的用户可以访问。"""
        app = _create_app(jwt_service, blacklist, rbac_policy=rbac_policy)
        token = jwt_service.create_access_token("admin-user", ["admin"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/write-config",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_permission_check_denied(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        rbac_policy: RBACPolicy,
    ):
        """测试无写权限的用户被拒绝。"""
        app = _create_app(jwt_service, blacklist, rbac_policy=rbac_policy)
        token = jwt_service.create_access_token("viewer-user", ["config_viewer"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/write-config",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_scope_check_allowed(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        rbac_policy: RBACPolicy,
    ):
        """测试有生产环境作用域的用户可以访问。"""
        app = _create_app(jwt_service, blacklist, rbac_policy=rbac_policy)
        token = jwt_service.create_access_token("admin-user", ["admin"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/prod-access",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_scope_check_denied(
        self,
        jwt_service: JWTService,
        blacklist: InMemoryTokenBlacklist,
        rbac_policy: RBACPolicy,
    ):
        """测试无生产环境作用域的用户被拒绝。"""
        app = _create_app(jwt_service, blacklist, rbac_policy=rbac_policy)
        token = jwt_service.create_access_token("viewer-user", ["config_viewer"])

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.get(
                "/prod-access",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 403
