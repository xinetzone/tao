"""Tests for OAuth services."""

import pytest

from taolib.testing.oauth.crypto.token_encryption import TokenEncryptor
from taolib.testing.oauth.errors import OAuthAlreadyLinkedError, OAuthCannotUnlinkError
from taolib.testing.oauth.models.enums import OAuthConnectionStatus, OAuthProvider
from taolib.testing.oauth.models.profile import OAuthUserInfo
from taolib.testing.oauth.repository.activity_repo import OAuthActivityLogRepository
from taolib.testing.oauth.repository.connection_repo import OAuthConnectionRepository
from taolib.testing.oauth.repository.credential_repo import OAuthAppCredentialRepository
from taolib.testing.oauth.repository.session_repo import OAuthSessionRepository
from taolib.testing.oauth.services.account_service import OAuthAccountService
from taolib.testing.oauth.services.admin_service import OAuthAdminService
from taolib.testing.oauth.services.session_service import OAuthSessionService


class TestAccountService:
    @pytest.fixture
    def encryptor(self, encryption_key):
        return TokenEncryptor(encryption_key)

    @pytest.fixture
    def service(self, mock_connection_collection, mock_activity_collection, encryptor):
        conn_repo = OAuthConnectionRepository(mock_connection_collection)
        activity_repo = OAuthActivityLogRepository(mock_activity_collection)
        return OAuthAccountService(
            connection_repo=conn_repo,
            activity_repo=activity_repo,
            token_encryptor=encryptor,
        )

    @pytest.mark.asyncio
    async def test_find_or_create_new_connection(self, service):
        user_info = OAuthUserInfo(
            provider=OAuthProvider.GOOGLE,
            provider_user_id="g-new-user",
            email="new@gmail.com",
            display_name="New User",
        )
        token_data = {
            "access_token": "access-123",
            "refresh_token": "refresh-123",
            "expires_in": 3600,
        }
        connection, is_new = await service.find_or_create_connection(
            user_info=user_info,
            token_data=token_data,
        )
        assert is_new is True
        assert connection is not None
        assert connection.status == OAuthConnectionStatus.PENDING_ONBOARDING

    @pytest.mark.asyncio
    async def test_find_or_create_existing_connection(self, service, encryptor):
        user_info = OAuthUserInfo(
            provider=OAuthProvider.GOOGLE,
            provider_user_id="g-existing",
            email="existing@gmail.com",
            display_name="Existing",
        )
        token_data = {"access_token": "token-1"}

        # First call creates
        conn1, is_new1 = await service.find_or_create_connection(
            user_info=user_info, token_data=token_data
        )
        assert is_new1 is True

        # Update to active status so it behaves like a returning user
        await service._connection_repo.update(
            conn1.id,
            {
                "user_id": "user-1",
                "status": str(OAuthConnectionStatus.ACTIVE),
            },
        )

        # Second call finds existing
        conn2, is_new2 = await service.find_or_create_connection(
            user_info=user_info, token_data={"access_token": "token-2"}
        )
        assert is_new2 is False

    @pytest.mark.asyncio
    async def test_link_provider(self, service):
        user_info = OAuthUserInfo(
            provider=OAuthProvider.GITHUB,
            provider_user_id="gh-link-test",
            email="link@example.com",
            display_name="Link User",
        )
        connection = await service.link_provider(
            user_id="user-1",
            user_info=user_info,
            token_data={"access_token": "token-link"},
        )
        assert connection is not None
        assert connection.user_id == "user-1"
        assert connection.status == OAuthConnectionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_link_provider_already_linked(self, service):
        user_info = OAuthUserInfo(
            provider=OAuthProvider.GITHUB,
            provider_user_id="gh-dup",
            email="dup@example.com",
            display_name="Dup",
        )
        await service.link_provider(
            user_id="user-1",
            user_info=user_info,
            token_data={"access_token": "t1"},
        )
        with pytest.raises(OAuthAlreadyLinkedError):
            await service.link_provider(
                user_id="user-1",
                user_info=user_info,
                token_data={"access_token": "t2"},
            )

    @pytest.mark.asyncio
    async def test_unlink_provider(self, service):
        user_info = OAuthUserInfo(
            provider=OAuthProvider.GOOGLE,
            provider_user_id="g-unlink",
            email="unlink@example.com",
        )
        await service.link_provider(
            user_id="user-1",
            user_info=user_info,
            token_data={"access_token": "t"},
        )
        result = await service.unlink_provider(
            user_id="user-1",
            provider="google",
            has_password=True,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_unlink_last_provider_without_password(self, service):
        user_info = OAuthUserInfo(
            provider=OAuthProvider.GOOGLE,
            provider_user_id="g-last",
            email="last@example.com",
        )
        await service.link_provider(
            user_id="user-1",
            user_info=user_info,
            token_data={"access_token": "t"},
        )
        with pytest.raises(OAuthCannotUnlinkError):
            await service.unlink_provider(
                user_id="user-1",
                provider="google",
                has_password=False,
            )

    @pytest.mark.asyncio
    async def test_get_user_connections(self, service):
        for prov, pid in [("google", "g-1"), ("github", "gh-1")]:
            user_info = OAuthUserInfo(
                provider=prov,
                provider_user_id=pid,
                email=f"{prov}@example.com",
            )
            await service.link_provider(
                user_id="user-1",
                user_info=user_info,
                token_data={"access_token": "t"},
            )
        connections = await service.get_user_connections("user-1")
        assert len(connections) == 2


class TestSessionService:
    @pytest.fixture
    def service(self, mock_session_collection, mock_redis, jwt_secret, jwt_algorithm):
        session_repo = OAuthSessionRepository(mock_session_collection)
        return OAuthSessionService(
            session_repo=session_repo,
            redis_client=mock_redis,
            jwt_secret=jwt_secret,
            jwt_algorithm=jwt_algorithm,
        )

    @pytest.mark.asyncio
    async def test_create_session(self, service):
        result = await service.create_session(
            user_id="user-1",
            connection_id="conn-1",
            provider="google",
            roles=["config_viewer"],
            ip_address="127.0.0.1",
        )
        assert "session_id" in result
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_validate_session(self, service):
        result = await service.create_session(
            user_id="user-1",
            connection_id="conn-1",
            provider="google",
            roles=[],
        )
        session = await service.validate_session(result["session_id"])
        assert session is not None
        assert session.user_id == "user-1"

    @pytest.mark.asyncio
    async def test_validate_invalid_session(self, service):
        session = await service.validate_session("nonexistent")
        assert session is None

    @pytest.mark.asyncio
    async def test_revoke_session(self, service):
        result = await service.create_session(
            user_id="user-1",
            connection_id="conn-1",
            provider="google",
            roles=[],
        )
        revoked = await service.revoke_session(result["session_id"])
        assert revoked is True

        # Should no longer be valid
        session = await service.validate_session(result["session_id"])
        assert session is None

    @pytest.mark.asyncio
    async def test_revoke_all_sessions(self, service):
        for i in range(3):
            await service.create_session(
                user_id="user-1",
                connection_id=f"conn-{i}",
                provider="google",
                roles=[],
            )
        count = await service.revoke_all_sessions("user-1")
        assert count == 3

    @pytest.mark.asyncio
    async def test_list_active_sessions(self, service):
        for i in range(2):
            await service.create_session(
                user_id="user-1",
                connection_id=f"conn-{i}",
                provider="google",
                roles=[],
            )
        sessions = await service.list_active_sessions("user-1")
        assert len(sessions) == 2


class TestAdminService:
    @pytest.fixture
    def encryptor(self, encryption_key):
        return TokenEncryptor(encryption_key)

    @pytest.fixture
    def service(
        self,
        mock_credential_collection,
        mock_activity_collection,
        mock_connection_collection,
        encryptor,
    ):
        return OAuthAdminService(
            credential_repo=OAuthAppCredentialRepository(mock_credential_collection),
            activity_repo=OAuthActivityLogRepository(mock_activity_collection),
            connection_repo=OAuthConnectionRepository(mock_connection_collection),
            token_encryptor=encryptor,
        )

    @pytest.mark.asyncio
    async def test_create_credential(self, service):
        from taolib.testing.oauth.models.credential import OAuthAppCredentialCreate

        data = OAuthAppCredentialCreate(
            provider="google",
            client_id="goog-id",
            client_secret="goog-secret",
            display_name="Google OAuth",
            redirect_uri="http://localhost/callback/google",
            allowed_scopes=["openid", "email"],
        )
        result = await service.create_credential(data, admin_user_id="admin-1")
        assert result.client_id == "goog-id"
        assert result.provider == "google"

    @pytest.mark.asyncio
    async def test_list_credentials(self, service):
        from taolib.testing.oauth.models.credential import OAuthAppCredentialCreate

        for prov in ["google", "github"]:
            data = OAuthAppCredentialCreate(
                provider=prov,
                client_id=f"{prov}-id",
                client_secret=f"{prov}-secret",
                redirect_uri=f"http://localhost/callback/{prov}",
            )
            await service.create_credential(data, admin_user_id="admin-1")
        creds = await service.list_credentials()
        assert len(creds) == 2

    @pytest.mark.asyncio
    async def test_delete_credential(self, service):
        from taolib.testing.oauth.models.credential import OAuthAppCredentialCreate

        data = OAuthAppCredentialCreate(
            provider="google",
            client_id="del-id",
            client_secret="del-secret",
            redirect_uri="http://localhost/callback/google",
        )
        created = await service.create_credential(data, admin_user_id="admin-1")
        result = await service.delete_credential(created.id, admin_user_id="admin-1")
        assert result is True

    @pytest.mark.asyncio
    async def test_get_stats(self, service):
        stats = await service.get_stats()
        assert "total_connections" in stats
        assert "active_connections" in stats



