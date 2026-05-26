"""多智能体系统枚举类型。

定义多智能体系统中使用的各种枚举。
"""

from enum import StrEnum


class AgentStatus(StrEnum):
    """智能体状态。"""

    CREATED = "created"
    IDLE = "idle"
    BUSY = "busy"
    SLEEPING = "sleeping"
    ERROR = "error"
    DESTROYED = "destroyed"


class AgentType(StrEnum):
    """智能体类型。"""

    MAIN = "main"
    SUB = "sub"
    SPECIALIZED = "specialized"


class TaskStatus(StrEnum):
    """任务状态。"""

    PENDING = "pending"
    ANALYZING = "analyzing"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SkillType(StrEnum):
    """技能类型。"""

    CODE = "code"
    PROMPT = "prompt"
    HYBRID = "hybrid"


class SkillStatus(StrEnum):
    """技能状态。"""

    DRAFT = "draft"
    TESTING = "testing"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class MessageType(StrEnum):
    """消息类型。"""

    TASK_ASSIGN = "task_assign"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_ERROR = "task_error"
    SKILL_REQUEST = "skill_request"
    SKILL_RESPONSE = "skill_response"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ModelProvider(StrEnum):
    """模型提供商。"""

    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"


class ModelStatus(StrEnum):
    """模型状态。"""

    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    UNAVAILABLE = "unavailable"


class LoadBalanceStrategy(StrEnum):
    """负载均衡策略。"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
