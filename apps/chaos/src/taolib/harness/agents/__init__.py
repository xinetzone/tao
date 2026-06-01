"""Agent 定义层 - LangGraph Agent 基类与模板。

公开导出：

* :class:`AgentConfig` / :class:`LLMConfig` —— Agent 元配置；
* :class:`GraphAgent` —— LangGraph Agent 抽象基类；
* :class:`ReActAgent` / :class:`PlanAndExecuteAgent` / :class:`RouterAgent` —— 预置模板；
* :class:`AgentTemplate` 与 :func:`create_from_template` —— 模板枚举与工厂。
"""

from .graph_agent import (
    AgentConfig,
    AgentTool,
    GraphAgent,
    GraphSpec,
    LLMConfig,
    NodeFn,
    ReActAgent,
    ToolFn,
)
from .templates import (
    AgentTemplate,
    PlanAndExecuteAgent,
    RouterAgent,
    create_from_template,
    register_template,
)

__all__ = [
    "AgentConfig",
    "AgentTemplate",
    "AgentTool",
    "GraphAgent",
    "GraphSpec",
    "LLMConfig",
    "NodeFn",
    "PlanAndExecuteAgent",
    "ReActAgent",
    "RouterAgent",
    "ToolFn",
    "create_from_template",
    "register_template",
]
