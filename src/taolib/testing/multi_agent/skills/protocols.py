"""技能系统协议。

定义技能系统的核心协议和基类。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from taolib.testing.multi_agent.models import SkillParameter


class SkillExecutionContext:
    """技能执行上下文。"""

    def __init__(
        self,
        parameters: Dict[str, Any],
        llm_provider: Any = None,
        agent: Any = None,
    ):
        """初始化执行上下文。

        Args:
            parameters: 技能参数
            llm_provider: LLM提供商
            agent: 执行技能的智能体
        """
        self.parameters = parameters
        self.llm_provider = llm_provider
        self.agent = agent
        self.state: Dict[str, Any] = {}


class Skill(ABC):
    """技能协议。"""

    @property
    @abstractmethod
    def id(self) -> str:
        """技能ID。"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称。"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """技能描述。"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> list[SkillParameter]:
        """技能参数定义。"""
        pass

    @abstractmethod
    async def execute(self, context: SkillExecutionContext) -> Any:
        """执行技能。

        Args:
            context: 执行上下文

        Returns:
            Any: 执行结果
        """
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, list[str]]:
        """验证参数。

        Args:
            parameters: 要验证的参数

        Returns:
            tuple[bool, list[str]]: (是否有效, 错误列表)
        """
        errors = []

        for param in self.parameters:
            if param.required and param.name not in parameters:
                errors.append(f"Required parameter '{param.name}' is missing")
                continue

            if param.name in parameters:
                value = parameters[param.name]
                if param.type == "string" and not isinstance(value, str):
                    errors.append(f"Parameter '{param.name}' should be string")
                elif param.type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Parameter '{param.name}' should be number")
                elif param.type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Parameter '{param.name}' should be boolean")

        return len(errors) == 0, errors


class BaseSkill(Skill):
    """技能基类。"""

    def __init__(
        self,
        skill_id: str,
        name: str,
        description: str,
        parameters: list[SkillParameter],
    ):
        """初始化技能基类。

        Args:
            skill_id: 技能ID
            name: 技能名称
            description: 技能描述
            parameters: 技能参数定义
        """
        self._id = skill_id
        self._name = name
        self._description = description
        self._parameters = parameters

    @property
    def id(self) -> str:
        """技能ID。"""
        return self._id

    @property
    def name(self) -> str:
        """技能名称。"""
        return self._name

    @property
    def description(self) -> str:
        """技能描述。"""
        return self._description

    @property
    def parameters(self) -> list[SkillParameter]:
        """技能参数定义。"""
        return self._parameters
