import pytest

from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import EnvironmentKind, RequestedTokenStrategy


def test_settings_from_env_parses_private_key_file(tmp_path, monkeypatch):
    key_file = tmp_path / "app.pem"
    key_file.write_text(
        "-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GITHUB_APP_ID", "123")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "456")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY_FILE", str(key_file))
    monkeypatch.setenv("GITHUB_API_URL", "https://api.github.com")
    monkeypatch.setenv("GITHUB_APP_TOKEN_STRATEGY", "auto")

    settings = GitHubAppSettings.from_env()

    assert settings.app_id == "123"
    assert settings.installation_id == "456"
    assert settings.private_key.startswith("-----BEGIN PRIVATE KEY-----")
    assert settings.runtime_profile.environment is EnvironmentKind.CLOUD
    assert settings.default_strategy is RequestedTokenStrategy.AUTO


def test_settings_from_env_rejects_missing_private_key(monkeypatch):
    monkeypatch.setenv("GITHUB_APP_ID", "123")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "456")

    with pytest.raises(ValueError, match="private key"):
        GitHubAppSettings.from_env()
