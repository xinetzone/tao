# Task 1: 建立配置层与基础模型

**Files:**
- Create: `tests/github_app/test_config.py`
- Create: `src/taolib/github_app/__init__.py`
- Create: `src/taolib/github_app/models.py`
- Create: `src/taolib/github_app/errors.py`
- Create: `src/taolib/github_app/config.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: 写失败测试，锁定配置解析与环境识别接口**

```python
import pytest

from taolib.github_app.config import GitHubAppSettings
from taolib.github_app.models import EnvironmentKind, RequestedTokenStrategy


def test_settings_from_env_parses_private_key_file(tmp_path, monkeypatch):
    key_file = tmp_path / "app.pem"
    key_file.write_text("-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n")
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
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `uv run pytest tests/github_app/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'taolib.github_app'`

- [ ] **Step 3: 写最小实现与依赖声明**

```toml
[project]
dependencies = [
  "httpx>=0.27,<1",
  "PyJWT[crypto]>=2.10,<3",
]

[project.scripts]
taolib-github-app = "taolib.cli.github_app:main"
```

```python
# src/taolib/github_app/models.py
from dataclasses import dataclass
from enum import StrEnum


class RequestedTokenStrategy(StrEnum):
    AUTO = "auto"
    ENABLED = "enabled"
    DISABLED = "disabled"


class EnvironmentKind(StrEnum):
    CLOUD = "cloud"
    GHES = "ghes"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class GitHubRuntimeProfile:
    base_url: str
    environment: EnvironmentKind
```

```python
# src/taolib/github_app/config.py
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(slots=True)
class GitHubAppSettings:
    app_id: str
    installation_id: str
    private_key: str
    api_url: str
    default_strategy: RequestedTokenStrategy
    eager_refresh_seconds: int
    allow_header_fallback: bool
    runtime_profile: GitHubRuntimeProfile

    @classmethod
    def from_env(cls) -> "GitHubAppSettings":
        private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
        private_key_file = os.getenv("GITHUB_APP_PRIVATE_KEY_FILE")
        if not private_key and private_key_file:
            private_key = Path(private_key_file).read_text(encoding="utf-8")
        if not private_key:
            raise ValueError("GitHub App private key is required")

        api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")
        environment = EnvironmentKind.CLOUD if api_url.rstrip("/") == "https://api.github.com" else EnvironmentKind.GHES
        return cls(
            app_id=os.environ["GITHUB_APP_ID"],
            installation_id=os.environ["GITHUB_APP_INSTALLATION_ID"],
            private_key=private_key,
            api_url=api_url,
            default_strategy=RequestedTokenStrategy(os.getenv("GITHUB_APP_TOKEN_STRATEGY", "auto")),
            eager_refresh_seconds=int(os.getenv("GITHUB_APP_TOKEN_EAGER_REFRESH_SECONDS", "90")),
            allow_header_fallback=os.getenv("GITHUB_APP_ALLOW_HEADER_FALLBACK", "true").lower() == "true",
            runtime_profile=GitHubRuntimeProfile(base_url=api_url, environment=environment),
        )
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `uv run pytest tests/github_app/test_config.py -v`
Expected: PASS with `2 passed`

- [ ] **Step 5: 提交本任务**

```bash
git add pyproject.toml src/taolib/github_app/__init__.py src/taolib/github_app/models.py src/taolib/github_app/errors.py src/taolib/github_app/config.py tests/github_app/test_config.py
git commit -m "feat: add github app configuration layer"
```
