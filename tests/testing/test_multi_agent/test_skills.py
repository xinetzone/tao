"""技能系统测试。

测试技能协议、注册表、管理器和预设技能。
"""

import pytest

from taolib.testing.multi_agent.errors import SkillError
from taolib.testing.multi_agent.models import SkillParameter, SkillStatus
from taolib.testing.multi_agent.skills import (
    BaseSkill,
    SkillExecutionContext,
    SkillManager,
    SkillRegistry,
    TextSummarizationSkill,
    CodeGenerationSkill,
    get_preset_skills,
    get_skill_manager,
    get_skill_registry,
)


class MockSkill(BaseSkill):
    """模拟技能，用于测试。"""

    def __init__(self):
        """初始化模拟技能。"""
        super().__init__(
            skill_id="mock_skill",
            name="模拟技能",
            description="这是一个模拟技能",
            parameters=[
                SkillParameter(
                    name="input",
                    type="string",
                    description="输入参数",
                    required=True,
                ),
                SkillParameter(
                    name="optional",
                    type="number",
                    description="可选参数",
                    required=False,
                    default=42,
                ),
            ],
        )

    async def execute(self, context: SkillExecutionContext) -> str:
        """执行技能。"""
        input_val = context.parameters["input"]
        optional_val = context.parameters.get("optional", 42)
        return f"Processed: {input_val} (optional: {optional_val})"


class TestSkillProtocols:
    """测试技能协议。"""

    def test_base_skill_initialization(self):
        """测试BaseSkill初始化。"""
        skill = MockSkill()
        assert skill.id == "mock_skill"
        assert skill.name == "模拟技能"
        assert skill.description == "这是一个模拟技能"
        assert len(skill.parameters) == 2

    def test_skill_parameter_validation_valid(self):
        """测试有效参数验证。"""
        skill = MockSkill()
        is_valid, errors = skill.validate_parameters({"input": "test"})
        assert is_valid is True
        assert len(errors) == 0

    def test_skill_parameter_validation_missing_required(self):
        """测试缺少必需参数。"""
        skill = MockSkill()
        is_valid, errors = skill.validate_parameters({})
        assert is_valid is False
        assert "Required parameter 'input' is missing" in errors

    def test_skill_parameter_validation_wrong_type(self):
        """测试参数类型错误。"""
        skill = MockSkill()
        is_valid, errors = skill.validate_parameters({"input": 123})
        assert is_valid is False
        assert "Parameter 'input' should be string" in errors

    @pytest.mark.asyncio
    async def test_skill_execution(self):
        """测试技能执行。"""
        skill = MockSkill()
        context = SkillExecutionContext(parameters={"input": "hello"})
        result = await skill.execute(context)
        assert result == "Processed: hello (optional: 42)"

    @pytest.mark.asyncio
    async def test_skill_execution_with_optional(self):
        """测试带可选参数的技能执行。"""
        skill = MockSkill()
        context = SkillExecutionContext(parameters={"input": "hello", "optional": 100})
        result = await skill.execute(context)
        assert result == "Processed: hello (optional: 100)"


class TestSkillRegistry:
    """测试技能注册表。"""

    @pytest.fixture
    def registry(self):
        """创建技能注册表。"""
        registry = SkillRegistry()
        registry.clear()
        return registry

    def test_register_skill(self, registry):
        """测试注册技能。"""
        skill = MockSkill()
        registry.register_skill(skill)
        assert registry.get_skill("mock_skill") is not None

    def test_register_duplicate_skill(self, registry):
        """测试注册重复技能。"""
        skill = MockSkill()
        registry.register_skill(skill)

        with pytest.raises(SkillError):
            registry.register_skill(skill)

    def test_get_skill_not_found(self, registry):
        """测试获取不存在的技能。"""
        skill = registry.get_skill("nonexistent")
        assert skill is None

    def test_get_all_skills(self, registry):
        """测试获取所有技能。"""
        skill1 = MockSkill()
        registry.register_skill(skill1)

        skills = registry.get_all_skills()
        assert len(skills) == 1

    def test_unregister_skill(self, registry):
        """测试注销技能。"""
        skill = MockSkill()
        registry.register_skill(skill)
        assert registry.get_skill("mock_skill") is not None

        registry.unregister_skill("mock_skill")
        assert registry.get_skill("mock_skill") is None

    def test_register_skill_class(self, registry):
        """测试注册技能类。"""
        registry.register_skill_class(MockSkill)
        skill_class = registry.get_skill_class("mock")
        assert skill_class is not None

    def test_global_registry(self):
        """测试全局注册表。"""
        registry = get_skill_registry()
        assert registry is not None


class TestSkillManager:
    """测试技能管理器。"""

    @pytest.fixture
    def manager(self):
        """创建技能管理器。"""
        registry = SkillRegistry()
        registry.clear()
        manager = SkillManager(registry=registry)
        manager._skill_documents.clear()
        manager._execution_history.clear()
        return manager

    def test_register_skill(self, manager):
        """测试注册技能。"""
        skill = MockSkill()
        manager.register_skill(skill)
        assert manager.get_skill("mock_skill") is not None
        assert manager.get_skill_document("mock_skill") is not None

    def test_list_skills(self, manager):
        """测试列出技能。"""
        skill = MockSkill()
        manager.register_skill(skill)

        skills = manager.list_skills()
        assert len(skills) == 1

        approved_skills = manager.list_skills(SkillStatus.APPROVED)
        assert len(approved_skills) == 1

    @pytest.mark.asyncio
    async def test_execute_skill(self, manager):
        """测试执行技能。"""
        skill = MockSkill()
        manager.register_skill(skill)

        result = await manager.execute_skill("mock_skill", {"input": "test"})
        assert result == "Processed: test (optional: 42)"

    @pytest.mark.asyncio
    async def test_execute_skill_not_found(self, manager):
        """测试执行不存在的技能。"""
        with pytest.raises(SkillError):
            await manager.execute_skill("nonexistent", {})

    @pytest.mark.asyncio
    async def test_execute_skill_invalid_params(self, manager):
        """测试执行技能时参数无效。"""
        skill = MockSkill()
        manager.register_skill(skill)

        with pytest.raises(SkillError):
            await manager.execute_skill("mock_skill", {})

    def test_get_execution_history(self, manager):
        """测试获取执行历史。"""
        history = manager.get_execution_history()
        assert len(history) == 0

    def test_global_manager(self):
        """测试全局管理器。"""
        manager = get_skill_manager()
        assert manager is not None


class TestPresetSkills:
    """测试预设技能。"""

    def test_get_preset_skills(self):
        """测试获取预设技能。"""
        skills = get_preset_skills()
        assert len(skills) == 4

    def test_text_summarization_skill(self):
        """测试文本摘要技能。"""
        skill = TextSummarizationSkill()
        assert skill.id == "text_summarization"
        assert skill.name == "文本摘要"

    def test_code_generation_skill(self):
        """测试代码生成技能。"""
        skill = CodeGenerationSkill()
        assert skill.id == "code_generation"
        assert skill.name == "代码生成"

    @pytest.mark.asyncio
    async def test_text_summarization_fallback(self):
        """测试文本摘要技能的回退机制。"""
        skill = TextSummarizationSkill()
        context = SkillExecutionContext(
            parameters={"text": "这是一段很长的文本" * 10, "max_length": 20}
        )
        result = await skill.execute(context)
        assert len(result) <= 23  # 20 + "..."

    @pytest.mark.asyncio
    async def test_code_generation_fallback(self):
        """测试代码生成技能的回退机制。"""
        skill = CodeGenerationSkill()
        context = SkillExecutionContext(
            parameters={"requirement": "写一个hello world", "language": "python"}
        )
        result = await skill.execute(context)
        assert "python" in result
        assert "hello world" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
