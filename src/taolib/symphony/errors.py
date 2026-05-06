"""Symphony 自定义异常。

定义编排服务中使用的异常层次结构。
"""


class SymphonyError(Exception):
    """所有 Symphony 错误的基类。"""

    pass


class ConfigError(SymphonyError):
    """配置相关错误。"""

    pass


class WorkflowLoadError(ConfigError):
    """WORKFLOW.md 解析失败。"""

    pass


class TrackerError(SymphonyError):
    """问题跟踪器相关错误。"""

    pass


class WorkspaceError(SymphonyError):
    """工作区相关错误。"""

    pass


class AgentError(SymphonyError):
    """Agent 相关错误。"""

    pass


class HookError(AgentError):
    """钩子执行失败。"""

    pass


class TransportError(AgentError):
    """传输层失败。"""

    pass


class PromptError(SymphonyError):
    """模板渲染失败。"""

    pass
