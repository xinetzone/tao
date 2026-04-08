"""Tests for OAuth models."""

from datetime import UTC, datetime

from taolib.testing.oauth.models.activity import (
    OAuthActivityLogDocument,
    OAuthActivityLogResponse,
)
from taolib.testing.oauth.models.connection import (
    OAuthConnectionDocument,
    OAuthConnectionResponse,
)
from taolib.testing.oauth.models.credential import (
    OAuthAppCredentialDocument,
    OAuthAppCredentialResponse,
)
from taolib.testing.oauth.models.enums import (
    OAuthActivityAction,
    OAuthActivityStatus,
    OAuthConnectionStatus,
    OAuthProvider,
)
from taolib.testing.oauth.models.profile import OAuthUserInfo, OnboardingData
from taolib.testing.oauth.models.session import OAuthSessionDocument, OAuthSessionResponse


class TestEnums:
    def test_oauth_provider_values(self):
        assert OAuthProvider.GOOGLE == "google"
        assert OAuthProvider.GITHUB == "github"

    def test_connection_status_values(self):
        assert OAuthConnectionStatus.ACTIVE == "active"
        assert OAuthConnectionStatus.REVOKED == "revoked"
        assert OAuthConnectionStatus.EXPIRED == "expired"
        assert OAuthConnectionStatus.PENDING_ONBOARDING == "pending_onboarding"

    def test_activity_action_values(self):
        assert OAuthActivityAction.LOGIN == "oauth.login"
        assert OAuthActivityAction.LINK == "oauth.link"

    def test_activity_status_values(self):
        assert OAuthActivityStatus.SUCCESS == "success"
        assert OAuthActivityStatus.FAILED == "failed"


class TestOAuthUserInfo:
    def test_create_user_info(self):
        info = OAuthUserInfo(
            provider=OAuthProvider.GOOGLE,
            provider_user_id="123",
            email="test@example.com",
            display_name="Test User",
            avatar_url="https://example.com/avatar.png",
        )
        assert info.provider == OAuthProvider.GOOGLE
        assert info.provider_user_id == "123"
        assert info.email == "test@example.com"
        assert info.display_name == "Test User"

    def test_user_info_defaults(self):
        info = OAuthUserInfo(
            provider=OAuthProvider.GITHUB,
            provider_user_id="456",
        )
        assert info.email is None
        assert info.display_name == ""
        assert info.avatar_url == ""
        assert info.raw_data == {}


class TestOnboardingData:
    def test_valid_onboarding(self):
        data = OnboardingData(username="newuser", display_name="New User")
        assert data.username == "newuser"
        assert data.display_name == "New User"

    def test_onboarding_defaults(self):
        data = OnboardingData(username="newuser")
        assert data.display_name is None


class TestConnectionDocument:
    def test_to_response(self):
        now = datetime.now(UTC)
        doc = OAuthConnectionDocument(
            _id="conn-1",
            provider=OAuthProvider.GOOGLE,
            provider_user_id="g-123",
            email="test@gmail.com",
            display_name="Test",
            avatar_url="https://example.com/avatar.png",
            user_id="user-1",
            access_token_encrypted="encrypted-token",
            status=OAuthConnectionStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        response = doc.to_response()
        assert isinstance(response, OAuthConnectionResponse)
        assert response.id == "conn-1"
        assert response.user_id == "user-1"
        assert response.provider == OAuthProvider.GOOGLE
        assert response.status == OAuthConnectionStatus.ACTIVE
        # Response should not have encrypted tokens
        assert not hasattr(response, "access_token_encrypted")


class TestCredentialDocument:
    def test_to_response(self):
        now = datetime.now(UTC)
        doc = OAuthAppCredentialDocument(
            _id="cred-1",
            provider=OAuthProvider.GITHUB,
            client_id="gh-client-id",
            client_secret_encrypted="encrypted-secret",
            display_name="GitHub OAuth",
            enabled=True,
            allowed_scopes=["user:email"],
            redirect_uri="http://localhost:8002/callback/github",
            created_by="admin-1",
            created_at=now,
            updated_at=now,
        )
        response = doc.to_response()
        assert isinstance(response, OAuthAppCredentialResponse)
        assert response.id == "cred-1"
        assert response.client_id == "gh-client-id"
        # Response should not have client_secret_encrypted
        assert not hasattr(response, "client_secret_encrypted")


class TestSessionDocument:
    def test_to_response(self):
        now = datetime.now(UTC)
        doc = OAuthSessionDocument(
            _id="sess-1",
            user_id="user-1",
            provider=OAuthProvider.GOOGLE,
            connection_id="conn-1",
            jwt_access_token="jwt-access",
            jwt_refresh_token="jwt-refresh",
            ip_address="127.0.0.1",
            user_agent="Test/1.0",
            is_active=True,
            created_at=now,
            expires_at=now,
            last_activity_at=now,
        )
        response = doc.to_response()
        assert isinstance(response, OAuthSessionResponse)
        assert response.id == "sess-1"
        assert response.is_active is True
        # Response should not have JWT tokens
        assert not hasattr(response, "jwt_access_token")


class TestActivityLogDocument:
    def test_to_response(self):
        now = datetime.now(UTC)
        doc = OAuthActivityLogDocument(
            _id="log-1",
            action=OAuthActivityAction.LOGIN,
            status=OAuthActivityStatus.SUCCESS,
            provider=OAuthProvider.GOOGLE,
            user_id="user-1",
            ip_address="127.0.0.1",
            timestamp=now,
        )
        response = doc.to_response()
        assert isinstance(response, OAuthActivityLogResponse)
        assert response.id == "log-1"
        assert response.action == OAuthActivityAction.LOGIN



