"""智能体测试。

测试智能体基类、主智能体和工厂。
"""

import asyncio
import pytest
import uuid
from datetime import UTC, datetime

from taolib.testing.multi_agent.agents import (
    BaseAgent,
    MainAgent,
    SubAgentWrapper,
    AgentFactory,
    get_agent_factory,
)
from taolib.testing.multi_agent.errors import AgentError
from taolib.testing.multi_agent.llm import LLMManager
from taolib.testing.multi_agent.models import LoadBalanceConfig, LoadBalanceStrategy
from taolib.testing.multi_agent.models import (
    AgentCapability,
    AgentCreate,
    AgentDocument,
    AgentStatus,
    AgentType,
    TaskDocument,
    TaskStatus,
)


class MockAgent(BaseAgent):
    """模拟智能体，用于测试。"""

    async def _handle_message(self, message):
        pass

    async def execute_task(self, task):
        pass


class TestBaseAgent:
    """测试智能体基类。"""

    @pytest.fixture
    def agent_document(self):
        """创建测试用智能体文档。"""
        return AgentDocument(
            _id=str(uuid.uuid4()),
            name="测试智能体",
            description="这是一个测试智能体",
            agent_type=AgentType.SUB,
            capabilities=[AgentCapability(name="测试", description="测试能力")],
            skills=[],
            tags=["测试"],
        )

    @pytest.fixture
    def task_document(self):
        """创建测试用任务文档。"""
        return TaskDocument(
            _id=str(uuid.uuid4()),
            name="测试任务",
            description="这是一个测试任务",
            status=TaskStatus.PENDING,
        )

    def test_initialization(self, agent_document):
        """测试初始化。"""
        agent = MockAgent(agent_document)
        assert agent.id == agent_document.id
        assert agent.name == agent_document.name
        assert agent.status == agent_document.status

    @pytest.mark.asyncio
    async def test_initialize(self, agent_document):
        """测试initialize方法。"""
        agent = MockAgent(agent_document)
        await agent.initialize()
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_assign_task(self, agent_document, task_document):
        """测试分配任务。"""
        agent = MockAgent(agent_document)
        await agent.initialize()
        await agent.assign_task(task_document)
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task.id == task_document.id

    @pytest.mark.asyncio
    async def test_assign_task_busy(self, agent_document, task_document):
        """测试忙碌时分配任务。"""
        agent = MockAgent(agent_document)
        await agent.initialize()
        await agent.assign_task(task_document)

        with pytest.raises(AgentError):
            await agent.assign_task(TaskDocument(_id=str(uuid.uuid4()), name="另一任务", description="", status=TaskStatus.PENDING))

    @pytest.mark.asyncio
    async def test_complete_task(self, agent_document, task_document):
        """测试完成任务。"""
        agent = MockAgent(agent_document)
        await agent.initialize()
        await agent.assign_task(task_document)
        await agent.complete_task(True, "结果")
        assert agent.status == AgentStatus.IDLE
        assert agent.current_task is None
        assert agent.document.completed_tasks == 1

    @pytest.mark.asyncio
    async def test_sleep(self, agent_document):
        """测试休眠。"""
        agent = MockAgent(agent_document)
        await agent.initialize()
        await agent.sleep()
        assert agent.status == AgentStatus.SLEEPING

    @pytest.mark.asyncio
    async def test_sleep_busy(self, agent_document, task_document):
        """测试忙碌时休眠。"""
        agent = MockAgent(agent_document)
        await agent.initialize()
        await agent.assign_task(task_document)

        with pytest.raises(AgentError):
            await agent.sleep()

    @pytest.mark.asyncio
    async def test_wake(self, agent_document):
        """测试唤醒。"""
        agent = MockAgent(agent_document)
        await agent.initialize()
        await agent.sleep()
        await agent.wake()
        assert agent.status == AgentStatus.IDLE


class TestAgentFactory:
    """测试智能体工厂。"""

    @pytest.fixture
    def llm_manager(self):
        """创建LLM管理器。"""
        config = LoadBalanceConfig(strategy=LoadBalanceStrategy.ROUND_ROBIN)
        return LLMManager(config)

    @pytest.fixture
    def agent_factory(self, llm_manager):
        """创建智能体工厂。"""
        return AgentFactory(llm_manager)

    def test_get_all_templates(self, agent_factory):
        """测试获取所有模板。"""
        templates = agent_factory.get_all_templates()
        assert len(templates) > 0
        assert "code_assistant" in templates

    def test_get_template(self, agent_factory):
        """测试获取模板。"""
        template = agent_factory.get_template("code_assistant")
        assert template is not None
        assert template.id == "code_assistant"

        template = agent_factory.get_template("nonexistent")
        assert template is None

    @pytest.mark.asyncio
    async def test_create_agent(self, agent_factory):
        """测试创建智能体。"""
        agent_create = AgentCreate(
            name="测试智能体",
            description="测试用智能体",
            agent_type=AgentType.SUB,
            capabilities=[AgentCapability(name="测试", description="测试能力")],
            skills=[],
            tags=["测试"],
        )

        agent = await agent_factory.create_agent(agent_create)
        assert agent is not None
        assert agent.name == "测试智能体"
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_create_agent_from_template(self, agent_factory):
        """测试从模板创建智能体。"""
        agent = await agent_factory.create_agent_from_template("code_assistant", "我的代码助手")
        assert agent is not None
        assert agent.name == "我的代码助手"
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_create_main_agent(self, agent_factory):
        """测试创建主智能体。"""
        agent = await agent_factory.create_main_agent("我的主智能体")
        assert isinstance(agent, MainAgent)
        assert agent.name == "我的主智能体"
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_global_factory(self):
        """测试全局工厂。"""
        factory = get_agent_factory()
        assert factory is not None
        templates = factory.get_all_templates()
        assert len(templates) > 0


class TestMainAgent:
    """测试主智能体。"""

    @pytest.fixture
    def llm_manager(self):
        """创建LLM管理器。"""
        config = LoadBalanceConfig(strategy=LoadBalanceStrategy.ROUND_ROBIN)
        return LLMManager(config)

    @pytest.fixture
    def agent_document(self):
        """创建测试用智能体文档。"""
        return AgentDocument(
            _id=str(uuid.uuid4()),
            name="主智能体",
            description="测试用主智能体",
            agent_type=AgentType.MAIN,
            capabilities=[
                AgentCapability(name="任务分析", description="分析任务需求"),
                AgentCapability(name="智能体调度", description="调度和管理子智能体"),
            ],
            skills=[],
            tags=["主智能体"],
        )

    @pytest.fixture
    def task_document(self):
        """创建测试用任务文档。"""
        return TaskDocument(
            _id=str(uuid.uuid4()),
            name="测试任务",
            description="这是一个测试任务",
            user_input="请帮我写一个Python脚本",
            status=TaskStatus.PENDING,
        )

    @pytest.mark.asyncio
    async def test_initialization(self, agent_document, llm_manager):
        """测试初始化。"""
        agent = MainAgent(agent_document, llm_manager)
        await agent.initialize()
        assert agent.status == AgentStatus.IDLE
        assert len(agent._sub_agents) > 0

    @pytest.mark.asyncio
    async def test_shutdown(self, agent_document, llm_manager):
        """测试关闭。"""
        agent = MainAgent(agent_document, llm_manager)
        await agent.initialize()
        await agent.shutdown()
        assert agent.status == AgentStatus.DESTROYED
        assert agent._is_running is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
