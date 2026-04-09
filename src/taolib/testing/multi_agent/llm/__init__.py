"""LLM模型集成模块。

提供无需API KEY的免费大模型集成。
"""

from taolib.testing.multi_agent.llm.load_balancer import LoadBalancer
from taolib.testing.multi_agent.llm.manager import LLMManager, get_llm_manager, set_llm_manager
from taolib.testing.multi_agent.llm.protocols import BaseLLMProvider, LLMProvider
from taolib.testing.multi_agent.llm.registry import ModelRegistry

__all__ = [
    "LLMProvider",
    "BaseLLMProvider",
    "ModelRegistry",
    "LoadBalancer",
    "LLMManager",
    "get_llm_manager",
    "set_llm_manager",
]
