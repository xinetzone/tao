# Task 1: Update Dependencies

**Files:**
- Modify: `pyproject.toml:15-19`

- [ ] **Step 1: Write the failing dependency import test**

Create `tests/github_app/test_pygithub_adapter.py`:
```python
def test_pygithub_is_installed():
    import github
    assert github.__name__ == "github"
```

- [ ] **Step 2: Run test to verify it fails (or might pass if already installed globally, but we want it in project)**

Run: `uv run pytest tests/github_app/test_pygithub_adapter.py -v`

- [ ] **Step 3: Modify `pyproject.toml`**

Modify `pyproject.toml` to include `PyGithub`:
```toml
[project.optional-dependencies]
github-app = [
  "httpx>=0.27,<1",
  "PyJWT[crypto]>=2.10,<3",
  "PyGithub>=2.5,<3",
]
```

- [ ] **Step 4: Sync dependencies and run test to verify it passes**

Run: `uv sync`
Run: `uv run pytest tests/github_app/test_pygithub_adapter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock tests/github_app/test_pygithub_adapter.py
git commit -m "build: add PyGithub to github-app optional dependencies"
```
