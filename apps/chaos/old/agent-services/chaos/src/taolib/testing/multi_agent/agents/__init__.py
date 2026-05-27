"""多智能体系统 - 智能体模块。

包含智能体基类、主智能体、子智能体和工厂类。
"""

from taolib.testing.multi_agent.agents.base import BaseAgent
from taolib.testing.multi_agent.agents.factory import (
    AgentFactory,
    get_agent_factory,
    set_agent_factory,
)
from taolib.testing.multi_agent.agents.main_agent import MainAgent, SubAgentWrapper
from taolib.testing.multi_agent.agents.templates import (
    AgentTemplate,
    get_all_templates,
    get_template,
)

__all__ = [
    # Base
    "BaseAgent",
    # Main Agent
    "MainAgent",
    "SubAgentWrapper",
    # Factory
    "AgentFactory",
    "get_agent_factory",
    "set_agent_factory",
    # Templates
    "AgentTemplate",
    "get_template",
    "get_all_templates",
]
