"""智能体工厂。

用于创建各种类型的智能体。
"""

import uuid
from typing import Dict, Optional, Type

from taolib.testing.multi_agent.agents.base import BaseAgent
from taolib.testing.multi_agent.agents.main_agent import MainAgent, SubAgentWrapper
from taolib.testing.multi_agent.agents.templates import (
    AgentTemplate,
    get_all_templates,
    get_template,
)
from taolib.testing.multi_agent.errors import AgentError
from taolib.testing.multi_agent.llm import LLMManager, get_llm_manager
from taolib.testing.multi_agent.models import (
    AgentCapability,
    AgentCreate,
    AgentDocument,
    AgentStatus,
    AgentType,
)


class AgentFactory:
    """智能体工厂。"""

    def __init__(self, llm_manager: Optional[LLMManager] = None):
        """初始化智能体工厂。

        Args:
            llm_manager: LLM管理器,如果为None则使用全局管理器
        """
        self._llm_manager = llm_manager or get_llm_manager()
        self._templates: Dict[str, AgentTemplate] = {}
        self._agent_classes: Dict[AgentType, Type[BaseAgent]] = {
            AgentType.MAIN: MainAgent,
            AgentType.SUB: SubAgentWrapper,
        }

        # 加载默认模板
        for template in get_all_templates():
            self._templates[template.id] = template

    def register_template(self, template: AgentTemplate) -> None:
        """注册智能体模板。

        Args:
            template: 智能体模板
        """
        self._templates[template.id] = template

    def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """获取智能体模板。

        Args:
            template_id: 模板ID

        Returns:
            Optional[AgentTemplate]: 模板,如果不存在则返回None
        """
        return self._templates.get(template_id)

    def get_all_templates(self) -> Dict[str, AgentTemplate]:
        """获取所有模板。

        Returns:
            Dict[str, AgentTemplate]: 所有模板的字典
        """
        return self._templates.copy()

    async def create_agent(
        self, agent_create: AgentCreate, agent_id: Optional[str] = None
    ) -> BaseAgent:
        """创建智能体。

        Args:
            agent_create: 智能体创建配置
            agent_id: 智能体ID,如果为None则自动生成

        Returns:
            BaseAgent: 创建的智能体

        Raises:
            AgentError: 无法创建智能体
        """
        if agent_id is None:
            agent_id = str(uuid.uuid4())

        # 创建文档
        agent_data = agent_create.model_dump()
        agent_data["status"] = AgentStatus.CREATED
        agent_data["current_task_id"] = None
        agent_data["completed_tasks"] = 0
        agent_data["failed_tasks"] = 0

        agent_doc = AgentDocument(
            _id=agent_id,
            **agent_data,
        )

        # 获取智能体类
        agent_class = self._agent_classes.get(agent_create.agent_type)
        if agent_class is None:
            agent_class = SubAgentWrapper

        # 创建智能体
        if agent_class == MainAgent:
            agent = MainAgent(agent_doc, self._llm_manager)
        else:
            agent = SubAgentWrapper(agent_doc, self._llm_manager)

        # 初始化智能体
        await agent.initialize()

        return agent

    async def create_agent_from_template(
        self, template_id: str, agent_name: Optional[str] = None, agent_id: Optional[str] = None
    ) -> BaseAgent:
        """从模板创建智能体。

        Args:
            template_id: 模板ID
            agent_name: 智能体名称,如果为None则使用模板名称
            agent_id: 智能体ID,如果为None则自动生成

        Returns:
            BaseAgent: 创建的智能体

        Raises:
            AgentError: 模板不存在
        """
        template = self.get_template(template_id)
        if template is None:
            raise AgentError(f"Template {template_id} not found")

        agent_create = AgentCreate(
            name=agent_name or template.name,
            description=template.description,
            agent_type=template.agent_type,
            capabilities=template.capabilities,
            config=template.config,
            skills=template.skills,
            tags=template.tags,
        )

        return await self.create_agent(agent_create, agent_id)

    async def create_main_agent(
        self, name: str = "主智能体", agent_id: Optional[str] = None
    ) -> MainAgent:
        """创建主智能体。

        Args:
            name: 智能体名称
            agent_id: 智能体ID,如果为None则自动生成

        Returns:
            MainAgent: 创建的主智能体
        """
        template = get_template("general_assistant")
        if template:
            agent_create = AgentCreate(
                name=name,
                description=template.description,
                agent_type=AgentType.MAIN,
                capabilities=template.capabilities,
                config=template.config,
                skills=template.skills,
                tags=template.tags,
            )
        else:
            agent_create = AgentCreate(
                name=name,
                description="多智能体系统主智能体",
                agent_type=AgentType.MAIN,
                capabilities=[
                    AgentCapability(name="任务分析", description="分析任务需求"),
                    AgentCapability(name="智能体调度", description="调度和管理子智能体"),
                    AgentCapability(name="结果聚合", description="聚合子任务结果"),
                ],
                skills=[],
                tags=["主智能体"],
            )

        agent = await self.create_agent(agent_create, agent_id)
        if not isinstance(agent, MainAgent):
            raise AgentError("Failed to create main agent")

        return agent


# 全局工厂实例
_global_factory: Optional[AgentFactory] = None


def get_agent_factory() -> AgentFactory:
    """获取全局智能体工厂。

    Returns:
        AgentFactory: 智能体工厂
    """
    global _global_factory
    if _global_factory is None:
        _global_factory = AgentFactory()
    return _global_factory


def set_agent_factory(factory: AgentFactory) -> None:
    """设置全局智能体工厂。

    Args:
        factory: 智能体工厂
    """
    global _global_factory
    _global_factory = factory
