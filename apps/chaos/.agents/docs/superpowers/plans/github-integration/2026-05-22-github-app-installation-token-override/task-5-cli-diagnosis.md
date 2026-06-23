# Task 5: 增加 CLI 双入口与脱敏诊断输出

**Files:**
- Create: `tests/github_app/test_cli.py`
- Create: `src/taolib/cli/__init__.py`
- Create: `src/taolib/cli/github_app.py`
- Modify: `src/taolib/github_app/__init__.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: 写失败测试，锁定 `token` 与 `profile` 子命令**

```python
import pytest

from taolib.cli.github_app import build_parser, main


class FakeManager:
    async def get_token(self, _request):
        return {"token_preview": "ghs_abcd...wxyz", "effective_strategy": "enabled"}


def test_profile_command_outputs_environment_summary(capsys, monkeypatch):
    monkeypatch.setenv("GITHUB_API_URL", "https://api.github.com")
    exit_code = main(["profile"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert '"environment": "cloud"' in out


def test_token_command_masks_secret(capsys, monkeypatch):
    monkeypatch.setattr("taolib.cli.github_app.build_manager", lambda args: FakeManager())
    exit_code = main(["token", "--installation-id", "456", "--strategy", "enabled"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "ghs_" in out
    assert "secret-full-value" not in out
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `uv run pytest tests/github_app/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'taolib.cli'`

- [ ] **Step 3: 写最小实现**

```python
# src/taolib/cli/github_app.py
import argparse
import asyncio
import json

from taolib.github_app import GitHubAppSettings, GitHubInstallationTokenManager, InstallationTokenRequest, RequestedTokenStrategy
from taolib.github_app.cache import InMemoryInstallationTokenCache
from taolib.github_app.client import GitHubAppClient

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taolib-github-app")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("profile")
    token_parser = subparsers.add_parser("token")
    token_parser.add_argument("--installation-id")
    token_parser.add_argument("--strategy", choices=["auto", "enabled", "disabled"], default="auto")
    return parser


def build_manager(args: argparse.Namespace) -> GitHubInstallationTokenManager:
    settings = GitHubAppSettings.from_env()
    client = GitHubAppClient(app_id=settings.app_id, private_key=settings.private_key, api_url=settings.api_url)
    return GitHubInstallationTokenManager(client=client, cache=InMemoryInstallationTokenCache(), settings=settings)


def build_request(args: argparse.Namespace) -> InstallationTokenRequest:
    return InstallationTokenRequest(
        installation_id=args.installation_id or GitHubAppSettings.from_env().installation_id,
        permissions={},
        repositories=[],
        strategy=RequestedTokenStrategy(args.strategy),
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "profile":
        settings = GitHubAppSettings.from_env()
        print(json.dumps({"environment": settings.runtime_profile.environment.value, "api_url": settings.api_url}))
        return 0
    manager = build_manager(args)
    result = asyncio.run(manager.get_token(build_request(args)))
    print(json.dumps(result))
    return 0
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `uv run pytest tests/github_app/test_cli.py -v`
Expected: PASS with `2 passed`

- [ ] **Step 5: 提交本任务**

```bash
git add pyproject.toml src/taolib/cli/__init__.py src/taolib/cli/github_app.py src/taolib/github_app/__init__.py tests/github_app/test_cli.py
git commit -m "feat: add github app cli"
```
