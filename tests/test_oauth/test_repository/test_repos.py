"""Tests for OAuth repositories."""

import pytest

from taolib.oauth.repository.activity_repo import OAuthActivityLogRepository
from taolib.oauth.repository.connection_repo import OAuthConnectionRepository
from taolib.oauth.repository.credential_repo import OAuthAppCredentialRepository
from taolib.oauth.repository.session_repo import OAuthSessionRepository


class TestConnectionRepository:
    @pytest.fixture
    def repo(self, mock_connection_collection):
        return OAuthConnectionRepository(mock_connection_collection)

    @pytest.mark.asyncio
    async def test_create_and_find(self, repo):
        doc_data = {
            "provider": "google",
            "provider_user_id": "g-123",
            "email": "test@gmail.com",
            "display_name": "Test User",
            "avatar_url": "",
            "user_id": "user-1",
            "access_token_encrypted": "enc-token",
            "status": "active",
        }
        created = await repo.create(doc_data)
        assert created is not None
        assert created.id is not None

    @pytest.mark.asyncio
    async def test_find_by_provider_user_id(self, repo):
        await repo.create(
            {
                "provider": "google",
                "provider_user_id": "g-123",
                "user_id": "user-1",
                "access_token_encrypted": "enc",
                "status": "active",
            }
        )
        found = await repo.find_by_provider_user_id("google", "g-123")
        assert found is not None
        assert found.provider_user_id == "g-123"

    @pytest.mark.asyncio
    async def test_find_by_provider_user_id_not_found(self, repo):
        found = await repo.find_by_provider_user_id("google", "nonexistent")
        assert found is None

    @pytest.mark.asyncio
    async def test_find_by_user_and_provider(self, repo):
        await repo.create(
            {
                "provider": "github",
                "provider_user_id": "gh-456",
                "user_id": "user-1",
                "access_token_encrypted": "enc",
                "status": "active",
            }
        )
        found = await repo.find_by_user_and_provider("user-1", "github")
        assert found is not None
        assert found.provider == "github"

    @pytest.mark.asyncio
    async def test_find_all_for_user(self, repo):
        for provider in ["google", "github"]:
            await repo.create(
                {
                    "provider": provider,
                    "provider_user_id": f"{provider}-123",
                    "user_id": "user-1",
                    "access_token_encrypted": "enc",
                    "status": "active",
                }
            )
        all_conns = await repo.find_all_for_user("user-1")
        assert len(all_conns) == 2

    @pytest.mark.asyncio
    async def test_count_active_for_user(self, repo):
        await repo.create(
            {
                "provider": "google",
                "provider_user_id": "g-1",
                "user_id": "user-1",
                "access_token_encrypted": "enc",
                "status": "active",
            }
        )
        await repo.create(
            {
                "provider": "github",
                "provider_user_id": "gh-1",
                "user_id": "user-1",
                "access_token_encrypted": "enc",
                "status": "revoked",
            }
        )
        count = await repo.count_active_for_user("user-1")
        assert count == 1

    @pytest.mark.asyncio
    async def test_create_indexes(self, repo):
        await repo.create_indexes()
        assert len(repo._collection.indexes) > 0


class TestCredentialRepository:
    @pytest.fixture
    def repo(self, mock_credential_collection):
        return OAuthAppCredentialRepository(mock_credential_collection)

    @pytest.mark.asyncio
    async def test_create_and_find_by_provider(self, repo):
        await repo.create(
            {
                "provider": "google",
                "client_id": "goog-client-id",
                "client_secret_encrypted": "enc-secret",
                "display_name": "Google OAuth",
                "enabled": True,
                "allowed_scopes": ["openid", "email"],
                "redirect_uri": "http://localhost/callback/google",
                "created_by": "admin",
            }
        )
        found = await repo.find_by_provider("google")
        assert found is not None
        assert found.client_id == "goog-client-id"

    @pytest.mark.asyncio
    async def test_find_all(self, repo):
        for prov in ["google", "github"]:
            await repo.create(
                {
                    "provider": prov,
                    "client_id": f"{prov}-client",
                    "client_secret_encrypted": "enc",
                    "redirect_uri": f"http://localhost/callback/{prov}",
                    "created_by": "admin",
                }
            )
        all_creds = await repo.find_all()
        assert len(all_creds) == 2


class TestSessionRepository:
    @pytest.fixture
    def repo(self, mock_session_collection):
        return OAuthSessionRepository(mock_session_collection)

    @pytest.mark.asyncio
    async def test_create_session(self, repo):
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        await repo.create(
            {
                "_id": "sess-1",
                "user_id": "user-1",
                "provider": "google",
                "connection_id": "conn-1",
                "jwt_access_token": "jwt-a",
                "jwt_refresh_token": "jwt-r",
                "is_active": True,
                "created_at": now,
                "expires_at": now + timedelta(hours=24),
                "last_activity_at": now,
            }
        )
        session = await repo.get_by_id("sess-1")
        assert session is not None
        assert session.is_active is True

    @pytest.mark.asyncio
    async def test_find_active_sessions(self, repo):
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        for i in range(3):
            await repo.create(
                {
                    "_id": f"sess-{i}",
                    "user_id": "user-1",
                    "provider": "google",
                    "connection_id": "conn-1",
                    "jwt_access_token": f"jwt-a-{i}",
                    "jwt_refresh_token": f"jwt-r-{i}",
                    "is_active": i < 2,  # Two active, one inactive
                    "created_at": now,
                    "expires_at": now + timedelta(hours=24),
                    "last_activity_at": now,
                }
            )
        active = await repo.find_active_sessions("user-1")
        assert len(active) == 2

    @pytest.mark.asyncio
    async def test_deactivate_session(self, repo):
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        await repo.create(
            {
                "_id": "sess-1",
                "user_id": "user-1",
                "provider": "google",
                "connection_id": "conn-1",
                "jwt_access_token": "jwt-a",
                "jwt_refresh_token": "jwt-r",
                "is_active": True,
                "created_at": now,
                "expires_at": now + timedelta(hours=24),
                "last_activity_at": now,
            }
        )
        result = await repo.deactivate_session("sess-1")
        assert result is True


class TestActivityLogRepository:
    @pytest.fixture
    def repo(self, mock_activity_collection):
        return OAuthActivityLogRepository(mock_activity_collection)

    @pytest.mark.asyncio
    async def test_log_activity(self, repo):
        await repo.log_activity(
            action="oauth.login",
            status="success",
            provider="google",
            user_id="user-1",
            ip_address="127.0.0.1",
        )
        logs = await repo.query_logs(user_id="user-1")
        assert len(logs) == 1
        assert logs[0].action == "oauth.login"

    @pytest.mark.asyncio
    async def test_query_logs_with_filters(self, repo):
        for action in ["oauth.login", "oauth.link", "oauth.login"]:
            await repo.log_activity(
                action=action,
                status="success",
                provider="google",
                user_id="user-1",
            )
        logs = await repo.query_logs(action="oauth.login")
        assert len(logs) == 2

    @pytest.mark.asyncio
    async def test_get_stats(self, repo):
        for _ in range(3):
            await repo.log_activity(
                action="oauth.login",
                status="success",
                provider="google",
            )
        stats = await repo.get_stats()
        assert isinstance(stats, dict)
