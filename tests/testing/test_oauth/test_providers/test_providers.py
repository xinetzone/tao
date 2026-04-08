"""Tests for OAuth provider implementations."""

import pytest

from taolib.testing.oauth.providers import ProviderRegistry
from taolib.testing.oauth.providers.github import GitHubOAuthProvider
from taolib.testing.oauth.providers.google import GoogleOAuthProvider


class TestProviderRegistry:
    def test_get_registered_provider(self):
        registry = ProviderRegistry()
        google = registry.get("google")
        assert isinstance(google, GoogleOAuthProvider)

    def test_get_github_provider(self):
        registry = ProviderRegistry()
        github = registry.get("github")
        assert isinstance(github, GitHubOAuthProvider)

    def test_get_unregistered_raises(self):
        registry = ProviderRegistry()
        with pytest.raises(KeyError):
            registry.get("unknown-provider")

    def test_list_providers(self):
        registry = ProviderRegistry()
        providers = registry.list_providers()
        assert "google" in providers
        assert "github" in providers

    def test_register_custom_provider(self):
        registry = ProviderRegistry()

        class CustomProvider:
            provider_name = "custom"

            def get_authorize_url(self, **kwargs):
                return "https://custom.example.com/auth"

            async def exchange_code(self, **kwargs):
                return {}

            async def fetch_user_info(self, access_token):
                return None

            async def refresh_access_token(self, **kwargs):
                return {}

            async def revoke_token(self, access_token):
                return True

        registry.register(CustomProvider())
        assert "custom" in registry.list_providers()


class TestGoogleOAuthProvider:
    def test_get_authorize_url(self):
        provider = GoogleOAuthProvider()
        url = provider.get_authorize_url(
            client_id="test-client-id",
            redirect_uri="http://localhost/callback",
            state="random-state",
            scopes=["openid", "email", "profile"],
        )
        assert "accounts.google.com" in url
        assert "test-client-id" in url
        assert "random-state" in url
        assert "openid" in url

    def test_authorize_url_includes_offline_access(self):
        provider = GoogleOAuthProvider()
        url = provider.get_authorize_url(
            client_id="id",
            redirect_uri="http://localhost/callback",
            state="state",
            scopes=["openid"],
        )
        assert "access_type=offline" in url


class TestGitHubOAuthProvider:
    def test_get_authorize_url(self):
        provider = GitHubOAuthProvider()
        url = provider.get_authorize_url(
            client_id="gh-client-id",
            redirect_uri="http://localhost/callback",
            state="random-state",
            scopes=["user:email", "read:user"],
        )
        assert "github.com" in url
        assert "gh-client-id" in url
        assert "random-state" in url



