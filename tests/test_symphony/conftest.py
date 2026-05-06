"""Symphony 测试共享 fixtures。"""

from pathlib import Path

import pytest

from taolib.symphony.config.schema import TrackerConfig


@pytest.fixture
def tmp_workflow_file(tmp_path: Path) -> Path:
    """临时 WORKFLOW.md 文件（含 YAML 前置数据和正文）。"""
    path = tmp_path / "WORKFLOW.md"
    path.write_text(
        "---\n"
        "tracker:\n"
        "  kind: linear\n"
        "  api_key: $LINEAR_API_KEY\n"
        "  project_slug: test-proj\n"
        "polling:\n"
        "  interval_ms: 5000\n"
        "---\n"
        "\n"
        "# My Prompt\n"
        "Hello world\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def tmp_toml_file(tmp_path: Path) -> Path:
    """临时 symphony.toml 文件。"""
    path = tmp_path / "symphony.toml"
    path.write_text(
        '[defaults.tracker]\n'
        'kind = "linear"\n'
        'project_slug = "from-toml"\n',
        encoding="utf-8",
    )
    return path


@pytest.fixture
def sample_tracker_config() -> TrackerConfig:
    """示例 TrackerConfig 实例。"""
    return TrackerConfig(
        kind="linear",
        api_key="test-api-key",
        project_slug="test-slug",
    )


@pytest.fixture
def env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """设置测试所需的环境变量。"""
    monkeypatch.setenv("TEST_SYM_KEY", "my-key-123")
    monkeypatch.setenv("LINEAR_API_KEY", "lin_api_xxx")
