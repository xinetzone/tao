"""配置模型测试。"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from taolib.symphony.config.schema import (
    AgentConfig,
    CodexConfig,
    PollingConfig,
    ServerConfig,
    SymphonyConfig,
    TrackerConfig,
)


class TestSymphonyConfig:
    """测试 SymphonyConfig 及其子模型。"""

    def test_default_values(self) -> None:
        """所有默认值正确。"""
        cfg = SymphonyConfig()
        assert cfg.tracker.kind == "linear"
        assert cfg.tracker.endpoint == "https://api.linear.app/graphql"
        assert cfg.tracker.api_key == ""
        assert cfg.tracker.project_slug == ""
        assert cfg.polling.interval_ms == 30000
        assert cfg.agent.max_concurrent_agents == 10
        assert cfg.agent.max_turns == 20
        assert cfg.codex.command == "codex app-server"
        assert cfg.server.bind == "127.0.0.1"
        assert cfg.server.port is None
        assert cfg.workspace.root == Path("/tmp/symphony_workspaces")

    def test_tracker_config_required_fields(self) -> None:
        """tracker 关键字段可被显式设置且 kind 受约束。"""
        cfg = TrackerConfig(kind="linear", api_key="key", project_slug="slug")
        assert cfg.kind == "linear"
        assert cfg.api_key == "key"
        assert cfg.project_slug == "slug"

        with pytest.raises(ValidationError):
            TrackerConfig(kind="jira")  # type: ignore[call-arg]

    def test_polling_config_default(self) -> None:
        """interval_ms 默认值为 30000。"""
        cfg = PollingConfig()
        assert cfg.interval_ms == 30000

    def test_agent_config_constraints(self) -> None:
        """max_turns 必须大于 0。"""
        with pytest.raises(ValidationError):
            AgentConfig(max_turns=0)

    def test_codex_config_defaults(self) -> None:
        """command 和 timeout 默认值正确。"""
        cfg = CodexConfig()
        assert cfg.command == "codex app-server"
        assert cfg.turn_timeout_ms == 3600000
        assert cfg.read_timeout_ms == 5000
        assert cfg.stall_timeout_ms == 300000

    def test_server_config_defaults(self) -> None:
        """bind 和 port 默认值正确。"""
        cfg = ServerConfig()
        assert cfg.bind == "127.0.0.1"
        assert cfg.port is None


class TestTrackerConfig:
    """测试 TrackerConfig 独立行为。"""

    def test_active_states_default(self) -> None:
        """active_states 默认值正确。"""
        cfg = TrackerConfig()
        assert cfg.active_states == ["Todo", "In Progress"]

    def test_terminal_states_default(self) -> None:
        """terminal_states 默认值正确。"""
        cfg = TrackerConfig()
        assert cfg.terminal_states == [
            "Closed",
            "Cancelled",
            "Canceled",
            "Duplicate",
            "Done",
        ]
