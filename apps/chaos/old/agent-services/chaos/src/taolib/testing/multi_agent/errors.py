"""多智能体系统错误类。

定义系统中使用的各种异常类型。
"""


class MultiAgentError(Exception):
    """多智能体系统基础错误。"""

    pass


class LLMError(MultiAgentError):
    """LLM模型相关错误。"""

    pass


class ModelUnavailableError(LLMError):
    """模型不可用错误。"""

    pass


class ModelTimeoutError(LLMError):
    """模型超时错误。"""

    pass


class ModelRateLimitError(LLMError):
    """模型限流错误。"""

    pass


class AgentError(MultiAgentError):
    """智能体相关错误。"""

    pass


class AgentNotFoundError(AgentError):
    """智能体未找到错误。"""

    pass


class AgentBusyError(AgentError):
    """智能体忙碌错误。"""

    pass


class TaskError(MultiAgentError):
    """任务相关错误。"""

    pass


class TaskNotFoundError(TaskError):
    """任务未找到错误。"""

    pass


class TaskCancelledError(TaskError):
    """任务已取消错误。"""

    pass


class SkillError(MultiAgentError):
    """技能相关错误。"""

    pass


class SkillNotFoundError(SkillError):
    """技能未找到错误。"""

    pass


class SkillExecutionError(SkillError):
    """技能执行错误。"""

    pass


class MessageError(MultiAgentError):
    """消息相关错误。"""

    pass


class SecurityError(MultiAgentError):
    """安全相关错误。"""

    pass


class ContentFilterError(SecurityError):
    """内容过滤错误。"""

    pass
