# Task 3: Expose Interfaces in `__init__.py`

**Files:**
- Modify: `tests/github_app/test_pygithub_adapter.py`
- Modify: `src/taolib/github_app/__init__.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/github_app/test_pygithub_adapter.py`:
```python
def test_module_exports():
    import taolib.github_app

    assert hasattr(taolib.github_app, "PyGithubInstallationClientFactory")
    assert hasattr(taolib.github_app, "build_pygithub_client")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/github_app/test_pygithub_adapter.py::test_module_exports -v`
Expected: FAIL (AssertionError)

- [ ] **Step 3: Write minimal implementation**

Modify `src/taolib/github_app/__init__.py` to import and expose the new classes/functions.

Append the imports to the existing imports block:
```python
from taolib.github_app.pygithub_adapter import (
    PyGithubInstallationClientFactory,
    build_pygithub_client,
)
```

Update `__all__` array to include the new symbols:
```python
__all__ = [
    "EffectiveTokenStrategy",
    "EnvironmentKind",
    "GitHubAppClient",
    "GitHubAppClientError",
    "GitHubAppConfigurationError",
    "GitHubAppError",
    "GitHubAppSettings",
    "GitHubInstallationTokenManager",
    "GitHubRuntimeProfile",
    "InMemoryInstallationTokenCache",
    "InstallationTokenRequest",
    "InstallationTokenResult",
    "PyGithubInstallationClientFactory",
    "RequestedTokenStrategy",
    "TokenKind",
    "build_pygithub_client",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/github_app/test_pygithub_adapter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/taolib/github_app/__init__.py tests/github_app/test_pygithub_adapter.py
git commit -m "feat: expose PyGithub adapter interfaces"
```
