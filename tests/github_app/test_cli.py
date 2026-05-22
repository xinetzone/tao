from datetime import UTC, datetime, timedelta

from taolib.github_app.models import InstallationTokenResult, TokenKind


class FakeManager:
    async def get_token(self, _request):
        return InstallationTokenResult(
            token="ghs_secret-full-value",
            expires_at=datetime.now(tz=UTC) + timedelta(minutes=30),
            token_kind=TokenKind.STATEFUL,
            requested_strategy="enabled",
            effective_strategy="enabled",
            degraded=False,
        )


def test_profile_command_outputs_environment_summary(capsys, monkeypatch):
    monkeypatch.setenv("GITHUB_API_URL", "https://api.github.com")

    from taolib.cli.github_app import main

    exit_code = main(["profile"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert '"environment": "cloud"' in out


def test_token_command_masks_secret(capsys, monkeypatch):
    from taolib.cli.github_app import main

    monkeypatch.setattr(
        "taolib.cli.github_app.build_manager",
        lambda args: FakeManager(),
    )

    exit_code = main(["token", "--installation-id", "456", "--strategy", "enabled"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert '"token_preview": "ghs_sec...alue"' in out
    assert "ghs_secret-full-value" not in out
