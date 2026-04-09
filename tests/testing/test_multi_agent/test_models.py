"""多智能体系统模型测试。

测试所有核心数据模型。
"""

import pytest
from datetime import UTC, datetime, timedelta

from taolib.testing.multi_agent.models import (
    # Enums
    AgentStatus,
    AgentType,
    TaskStatus,
    SkillType,
    SkillStatus,
    MessageType,
    ModelProvider,
    ModelStatus,
    LoadBalanceStrategy,
    # Agent models
    AgentCapability,
    AgentConfig,
    AgentTemplate,
    AgentBase,
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentDocument,
    # Task models
    TaskConstraint,
    TaskProgress,
    TaskResult,
    SubTask,
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDocument,
    # Skill models
    SkillTestResult,
    SkillEvaluation,
    SkillParameter,
    SkillBase,
    SkillCreate,
    SkillUpdate,
    SkillResponse,
    SkillDocument,
    # Message models
    MessagePayload,
    Message,
    # LLM models
    ModelConfig,
    ModelStats,
    ModelInstance,
    LoadBalanceConfig,
)
from taolib.testing.multi_agent.agents.templates import (
    get_code_assistant_template,
    get_writing_assistant_template,
    get_all_templates,
)


class TestEnums:
    """测试枚举类型。"""

    def test_agent_status_enum(self):
        """测试智能体状态枚举。"""
        assert AgentStatus.IDLE == "idle"
        assert AgentStatus.BUSY == "busy"
        assert AgentStatus.SLEEPING == "sleeping"
        assert AgentStatus.ERROR == "error"
        assert AgentStatus.DESTROYED == "destroyed"

    def test_agent_type_enum(self):
        """测试智能体类型枚举。"""
        assert AgentType.MAIN == "main"
        assert AgentType.SUB == "sub"
        assert AgentType.SPECIALIZED == "specialized"

    def test_task_status_enum(self):
        """测试任务状态枚举。"""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.ANALYZING == "analyzing"
        assert TaskStatus.ASSIGNED == "assigned"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"

    def test_model_provider_enum(self):
        """测试模型提供商枚举。"""
        assert ModelProvider.OLLAMA == "ollama"
        assert ModelProvider.HUGGINGFACE == "huggingface"
        assert ModelProvider.GEMINI == "gemini"

    def test_load_balance_strategy_enum(self):
        """测试负载均衡策略枚举。"""
        assert LoadBalanceStrategy.ROUND_ROBIN == "round_robin"
        assert LoadBalanceStrategy.LEAST_CONNECTIONS == "least_connections"
        assert LoadBalanceStrategy.RANDOM == "random"
        assert LoadBalanceStrategy.WEIGHTED == "weighted"


class TestAgentModels:
    """测试智能体相关模型。"""

    def test_agent_capability(self):
        """测试智能体能力模型。"""
        capability = AgentCapability(
            name="代码生成",
            description="生成高质量代码",
            confidence=0.9,
            tags=["coding", "python"],
        )
        assert capability.name == "代码生成"
        assert capability.confidence == 0.9
        assert "coding" in capability.tags

    def test_agent_config(self):
        """测试智能体配置模型。"""
        config = AgentConfig(
            max_concurrent_tasks=3,
            timeout_seconds=300,
            temperature=0.7,
        )
        assert config.max_concurrent_tasks == 3
        assert config.timeout_seconds == 300
        assert config.temperature == 0.7

    def test_agent_base(self):
        """测试智能体基础模型。"""
        agent = AgentBase(
            name="测试智能体",
            description="这是一个测试智能体",
            agent_type=AgentType.SUB,
            status=AgentStatus.IDLE,
        )
        assert agent.name == "测试智能体"
        assert agent.agent_type == AgentType.SUB
        assert agent.status == AgentStatus.IDLE

    def test_agent_create_update(self):
        """测试智能体创建和更新模型。"""
        create = AgentCreate(
            name="新智能体",
            agent_type=AgentType.SPECIALIZED,
        )
        assert create.name == "新智能体"

        update = AgentUpdate(
            status=AgentStatus.BUSY,
            description="更新后的描述",
        )
        assert update.status == AgentStatus.BUSY
        assert update.description == "更新后的描述"

    def test_agent_document(self):
        """测试智能体文档模型。"""
        doc = AgentDocument(
            _id="test-agent-001",
            name="文档智能体",
            agent_type=AgentType.MAIN,
        )
        assert doc.id == "test-agent-001"
        assert doc.created_at is not None
        assert doc.updated_at is not None

        response = doc.to_response()
        assert response.id == "test-agent-001"


class TestTaskModels:
    """测试任务相关模型。"""

    def test_task_constraint(self):
        """测试任务约束模型。"""
        constraint = TaskConstraint(
            max_duration_seconds=3600,
            priority=8,
            required_skills=["skill-1", "skill-2"],
        )
        assert constraint.max_duration_seconds == 3600
        assert constraint.priority == 8
        assert len(constraint.required_skills) == 2

    def test_task_progress(self):
        """测试任务进度模型。"""
        progress = TaskProgress(
            current_step="执行中",
            progress_percent=50.0,
            completed_steps=["步骤1", "步骤2"],
        )
        assert progress.progress_percent == 50.0
        assert len(progress.completed_steps) == 2

    def test_task_result(self):
        """测试任务结果模型。"""
        result = TaskResult(
            success=True,
            summary="任务完成",
            details={"output": "test"},
        )
        assert result.success is True
        assert result.summary == "任务完成"

    def test_subtask(self):
        """测试子任务模型。"""
        subtask = SubTask(
            id="subtask-001",
            name="子任务1",
            status=TaskStatus.PENDING,
        )
        assert subtask.id == "subtask-001"
        assert subtask.status == TaskStatus.PENDING

    def test_task_document(self):
        """测试任务文档模型。"""
        doc = TaskDocument(
            _id="task-001",
            name="测试任务",
            user_input="请帮我完成这个任务",
        )
        assert doc.id == "task-001"
        assert doc.created_at is not None

        response = doc.to_response()
        assert response.id == "task-001"


class TestSkillModels:
    """测试技能相关模型。"""

    def test_skill_parameter(self):
        """测试技能参数模型。"""
        param = SkillParameter(
            name="input_text",
            type="str",
            description="输入文本",
            required=True,
        )
        assert param.name == "input_text"
        assert param.required is True

    def test_skill_test_result(self):
        """测试技能测试结果模型。"""
        test_result = SkillTestResult(
            test_name="基础测试",
            success=True,
            input_data={"text": "test"},
            actual_output={"result": "success"},
            execution_time_seconds=0.5,
        )
        assert test_result.success is True
        assert test_result.execution_time_seconds == 0.5

    def test_skill_evaluation(self):
        """测试技能评估模型。"""
        evaluation = SkillEvaluation(
            overall_score=0.85,
            accuracy=0.9,
            efficiency=0.8,
            reliability=0.85,
        )
        assert evaluation.overall_score == 0.85
        assert evaluation.accuracy == 0.9

    def test_skill_document(self):
        """测试技能文档模型。"""
        doc = SkillDocument(
            _id="skill-001",
            name="测试技能",
            skill_type=SkillType.PROMPT,
            status=SkillStatus.DRAFT,
            content="这是一个prompt技能",
        )
        assert doc.id == "skill-001"
        assert doc.skill_type == SkillType.PROMPT

        response = doc.to_response()
        assert response.id == "skill-001"


class TestMessageModels:
    """测试消息相关模型。"""

    def test_message_payload(self):
        """测试消息载荷模型。"""
        payload = MessagePayload(
            task_id="task-001",
            agent_id="agent-001",
            data={"key": "value"},
        )
        assert payload.task_id == "task-001"
        assert payload.data["key"] == "value"

    def test_message(self):
        """测试消息模型。"""
        message = Message(
            id="msg-001",
            message_type=MessageType.TASK_ASSIGN,
            sender_id="main-agent",
            receiver_id="sub-agent",
            priority=5,
        )
        assert message.id == "msg-001"
        assert message.message_type == MessageType.TASK_ASSIGN
        assert message.timestamp is not None


class TestLLMModels:
    """测试LLM相关模型。"""

    def test_model_config(self):
        """测试模型配置模型。"""
        config = ModelConfig(
            provider=ModelProvider.OLLAMA,
            model_name="llama2",
            base_url="http://localhost:11434",
            timeout_seconds=60,
            max_retries=3,
        )
        assert config.provider == ModelProvider.OLLAMA
        assert config.model_name == "llama2"
        assert config.timeout_seconds == 60

    def test_model_stats(self):
        """测试模型统计模型。"""
        stats = ModelStats(
            total_requests=100,
            successful_requests=95,
            failed_requests=5,
            average_latency_seconds=1.5,
        )
        assert stats.total_requests == 100
        assert stats.successful_requests == 95
        assert stats.average_latency_seconds == 1.5

    def test_model_instance(self):
        """测试模型实例模型。"""
        config = ModelConfig(
            provider=ModelProvider.HUGGINGFACE,
            model_name="gpt2",
        )
        instance = ModelInstance(
            id="model-001",
            config=config,
            status=ModelStatus.AVAILABLE,
        )
        assert instance.id == "model-001"
        assert instance.status == ModelStatus.AVAILABLE

    def test_load_balance_config(self):
        """测试负载均衡配置模型。"""
        config = LoadBalanceConfig(
            strategy=LoadBalanceStrategy.LEAST_CONNECTIONS,
            health_check_interval_seconds=30,
            circuit_breaker_enabled=True,
        )
        assert config.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS
        assert config.health_check_interval_seconds == 30


class TestAgentTemplates:
    """测试智能体模板。"""

    def test_code_assistant_template(self):
        """测试代码助手模板。"""
        template = get_code_assistant_template()
        assert template.name == "代码助手"
        assert template.agent_type == AgentType.SPECIALIZED
        assert len(template.capabilities) > 0
        assert template.config.system_prompt is not None

    def test_writing_assistant_template(self):
        """测试写作助手模板。"""
        template = get_writing_assistant_template()
        assert template.name == "写作助手"
        assert len(template.capabilities) > 0

    def test_all_templates(self):
        """测试获取所有模板。"""
        templates = get_all_templates()
        assert len(templates) >= 5
        template_names = [t.name for t in templates]
        assert "代码助手" in template_names
        assert "写作助手" in template_names
        assert "通用助手" in template_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
