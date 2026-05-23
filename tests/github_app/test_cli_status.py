"""status 子命令测试。"""

import json


def test_status_empty_cache(capsys, monkeypatch):
    """status 在缓存为空时应返回 cached=false。"""
    monkeypatch.setenv("GITHUB_APP_ID", "123")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "456")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\nfake\n-----END RSA PRIVATE KEY-----\n")

    from taolib.cli.github_app import main

    exit_code = main(["status", "--installation-id", "456"])
    out = capsys.readouterr().out

    assert exit_code == 0
    payload = json.loads(out)
    assert payload["cached"] is False
    assert payload["expired"] is False
    assert payload["expires_at"] is None
    assert payload["token_kind"] is None
