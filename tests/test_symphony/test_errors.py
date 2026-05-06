"""异常层级测试。"""

from taolib.symphony.errors import (
    AgentError,
    ConfigError,
    HookError,
    PromptError,
    SymphonyError,
    TrackerError,
    TransportError,
    WorkflowLoadError,
    WorkspaceError,
)


class TestErrorHierarchy:
    """测试异常继承关系。"""

    def test_config_error_is_symphony_error(self) -> None:
        """ConfigError 继承自 SymphonyError。"""
        assert issubclass(ConfigError, SymphonyError)

    def test_workflow_load_error_is_config_error(self) -> None:
        """WorkflowLoadError 继承自 ConfigError。"""
        assert issubclass(WorkflowLoadError, ConfigError)

    def test_hook_error_is_agent_error(self) -> None:
        """HookError 继承自 AgentError。"""
        assert issubclass(HookError, AgentError)

    def test_transport_error_is_agent_error(self) -> None:
        """TransportError 继承自 AgentError。"""
        assert issubclass(TransportError, AgentError)

    def test_prompt_error_is_symphony_error(self) -> None:
        """PromptError 继承自 SymphonyError。"""
        assert issubclass(PromptError, SymphonyError)

    def test_all_errors_are_exceptions(self) -> None:
        """所有自定义异常均继承自 Exception。"""
        errors = [
            SymphonyError,
            ConfigError,
            WorkflowLoadError,
            TrackerError,
            WorkspaceError,
            AgentError,
            HookError,
            TransportError,
            PromptError,
        ]
        for err in errors:
            assert issubclass(err, Exception)
