"""多智能体系统模型。

导出所有 Pydantic 模型和枚举。
"""

from taolib.testing.multi_agent.models.agent import (
    AgentBase,
    AgentCapability,
    AgentConfig,
    AgentCreate,
    AgentDocument,
    AgentResponse,
    AgentTemplate,
    AgentUpdate,
)
from taolib.testing.multi_agent.models.enums import (
    AgentStatus,
    AgentType,
    LoadBalanceStrategy,
    MessageType,
    ModelProvider,
    ModelStatus,
    SkillStatus,
    SkillType,
    TaskStatus,
)
from taolib.testing.multi_agent.models.llm import (
    LoadBalanceConfig,
    ModelConfig,
    ModelInstance,
    ModelStats,
)
from taolib.testing.multi_agent.models.message import Message, MessagePayload
from taolib.testing.multi_agent.models.skill import (
    SkillBase,
    SkillCreate,
    SkillDocument,
    SkillEvaluation,
    SkillParameter,
    SkillResponse,
    SkillTestResult,
    SkillUpdate,
)
from taolib.testing.multi_agent.models.task import (
    SubTask,
    TaskBase,
    TaskConstraint,
    TaskCreate,
    TaskDocument,
    TaskProgress,
    TaskResponse,
    TaskResult,
    TaskUpdate,
)

__all__ = [
    # Enums
    "AgentStatus",
    "AgentType",
    "TaskStatus",
    "SkillType",
    "SkillStatus",
    "MessageType",
    "ModelProvider",
    "ModelStatus",
    "LoadBalanceStrategy",
    # Agent models
    "AgentCapability",
    "AgentConfig",
    "AgentTemplate",
    "AgentBase",
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "AgentDocument",
    # Task models
    "TaskConstraint",
    "TaskProgress",
    "TaskResult",
    "SubTask",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskDocument",
    # Skill models
    "SkillTestResult",
    "SkillEvaluation",
    "SkillParameter",
    "SkillBase",
    "SkillCreate",
    "SkillUpdate",
    "SkillResponse",
    "SkillDocument",
    # Message models
    "MessagePayload",
    "Message",
    # LLM models
    "ModelConfig",
    "ModelStats",
    "ModelInstance",
    "LoadBalanceConfig",
]
