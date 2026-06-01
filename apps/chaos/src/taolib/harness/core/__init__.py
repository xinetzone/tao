"""核心层：桥接、状态管理与注册表。"""

from .bridge import (
    BridgeConfig,
    BridgeError,
    BridgeEvent,
    BridgeEventBus,
    BridgeEventKind,
    NodeOutput,
    NodeToStepAdapter,
    SerializationFormat,
    StepResult,
    StepToGraphAdapter,
)
from .registry import (
    AgentRegistry,
    FlowRegistry,
    RegistryEntry,
    UnifiedRegistry,
    get_default_registry,
    register_agent,
    register_flow,
)
from .state import (
    StateChangeEvent,
    StateChangeKind,
    StateListener,
    StateSnapshot,
    StateView,
    UnifiedStateManager,
)

__all__ = [
    "AgentRegistry",
    "BridgeConfig",
    "BridgeError",
    "BridgeEvent",
    "BridgeEventBus",
    "BridgeEventKind",
    "FlowRegistry",
    "NodeOutput",
    "NodeToStepAdapter",
    "RegistryEntry",
    "SerializationFormat",
    "StateChangeEvent",
    "StateChangeKind",
    "StateListener",
    "StateSnapshot",
    "StateView",
    "StepResult",
    "StepToGraphAdapter",
    "UnifiedRegistry",
    "UnifiedStateManager",
    "get_default_registry",
    "register_agent",
    "register_flow",
]
