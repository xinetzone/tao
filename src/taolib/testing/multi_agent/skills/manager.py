"""技能管理器。

统一管理技能的执行、评估和探索。
"""

from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from taolib.testing.multi_agent.errors import SkillError
from taolib.testing.multi_agent.llm import LLMManager, get_llm_manager
from taolib.testing.multi_agent.models import (
    SkillCreate,
    SkillDocument,
    SkillEvaluation,
    SkillStatus,
    SkillTestResult,
)
from taolib.testing.multi_agent.skills.protocols import (
    BaseSkill,
    Skill,
    SkillExecutionContext,
)
from taolib.testing.multi_agent.skills.registry import (
    SkillRegistry,
    get_skill_registry,
)


class SkillManager:
    """技能管理器。"""

    def __init__(
        self,
        registry: Optional[SkillRegistry] = None,
        llm_manager: Optional[LLMManager] = None,
    ):
        """初始化技能管理器。

        Args:
            registry: 技能注册表,如果为None则使用全局注册表
            llm_manager: LLM管理器,如果为None则使用全局管理器
        """
        self._registry = registry or get_skill_registry()
        self._llm_manager = llm_manager or get_llm_manager()
        self._skill_documents: Dict[str, SkillDocument] = {}
        self._execution_history: List[Dict[str, Any]] = []

    def register_skill(self, skill: Skill, document: Optional[SkillDocument] = None) -> None:
        """注册技能。

        Args:
            skill: 技能实例
            document: 技能文档,如果为None则自动创建

        Raises:
            SkillError: 技能已存在
        """
        self._registry.register_skill(skill)

        if document is None:
            document = SkillDocument(
                _id=skill.id,
                name=skill.name,
                description=skill.description,
                skill_type="prompt",
                parameters=skill.parameters,
                status=SkillStatus.APPROVED,
                code="",
                prompt_template="",
            )

        self._skill_documents[skill.id] = document

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """获取技能。

        Args:
            skill_id: 技能ID

        Returns:
            Optional[Skill]: 技能实例,如果不存在则返回None
        """
        return self._registry.get_skill(skill_id)

    def get_skill_document(self, skill_id: str) -> Optional[SkillDocument]:
        """获取技能文档。

        Args:
            skill_id: 技能ID

        Returns:
            Optional[SkillDocument]: 技能文档,如果不存在则返回None
        """
        return self._skill_documents.get(skill_id)

    def list_skills(self, status: Optional[SkillStatus] = None) -> List[SkillDocument]:
        """列出技能。

        Args:
            status: 技能状态过滤,如果为None则返回所有

        Returns:
            List[SkillDocument]: 技能文档列表
        """
        skills = list(self._skill_documents.values())
        if status:
            skills = [s for s in skills if s.status == status]
        return skills

    async def execute_skill(
        self,
        skill_id: str,
        parameters: Dict[str, Any],
        agent: Any = None,
    ) -> Any:
        """执行技能。

        Args:
            skill_id: 技能ID
            parameters: 技能参数
            agent: 执行技能的智能体

        Returns:
            Any: 执行结果

        Raises:
            SkillError: 技能不存在或执行失败
        """
        skill = self.get_skill(skill_id)
        if skill is None:
            raise SkillError(f"Skill '{skill_id}' not found")

        # 验证参数
        is_valid, errors = skill.validate_parameters(parameters)
        if not is_valid:
            raise SkillError(f"Invalid parameters: {', '.join(errors)}")

        # 创建执行上下文
        context = SkillExecutionContext(
            parameters=parameters,
            llm_provider=self._llm_manager,
            agent=agent,
        )

        # 记录执行开始
        start_time = datetime.now(UTC)
        execution_record = {
            "skill_id": skill_id,
            "parameters": parameters.copy(),
            "started_at": start_time,
            "success": False,
        }

        try:
            # 执行技能
            result = await skill.execute(context)

            # 记录成功
            execution_record["success"] = True
            execution_record["result"] = result
            execution_record["completed_at"] = datetime.now(UTC)

            return result

        except Exception as e:
            # 记录失败
            execution_record["success"] = False
            execution_record["error"] = str(e)
            execution_record["completed_at"] = datetime.now(UTC)
            raise SkillError(f"Skill execution failed: {e}") from e

        finally:
            # 保存执行记录
            self._execution_history.append(execution_record)

    async def test_skill(
        self,
        skill_id: str,
        test_cases: List[Dict[str, Any]],
    ) -> SkillTestResult:
        """测试技能。

        Args:
            skill_id: 技能ID
            test_cases: 测试用例列表,每个用例包含parameters和expected

        Returns:
            SkillTestResult: 测试结果
        """
        passed = 0
        failed = 0
        results: List[Dict[str, Any]] = []

        for i, test_case in enumerate(test_cases):
            parameters = test_case.get("parameters", {})
            expected = test_case.get("expected")

            try:
                actual = await self.execute_skill(skill_id, parameters)
                success = expected is None or actual == expected

                if success:
                    passed += 1
                else:
                    failed += 1

                results.append({
                    "test_case": i,
                    "success": success,
                    "parameters": parameters,
                    "expected": expected,
                    "actual": actual,
                })

            except Exception as e:
                failed += 1
                results.append({
                    "test_case": i,
                    "success": False,
                    "parameters": parameters,
                    "error": str(e),
                })

        total = passed + failed
        success_rate = passed / total if total > 0 else 0.0

        return SkillTestResult(
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            success_rate=success_rate,
            details=results,
        )

    async def evaluate_skill(
        self,
        skill_id: str,
        test_cases: Optional[List[Dict[str, Any]]] = None,
    ) -> SkillEvaluation:
        """评估技能。

        Args:
            skill_id: 技能ID
            test_cases: 测试用例,如果为None则使用文档中的测试用例

        Returns:
            SkillEvaluation: 评估结果
        """
        document = self.get_skill_document(skill_id)
        if document is None:
            raise SkillError(f"Skill document '{skill_id}' not found")

        # 如果没有提供测试用例,尝试从文档获取
        if test_cases is None and document.test_cases:
            test_cases = document.test_cases

        if not test_cases:
            test_cases = []

        # 执行测试
        test_result = await self.test_skill(skill_id, test_cases)

        # 计算分数
        score = test_result.success_rate * 100

        # 确定状态
        if score >= 90:
            status = SkillStatus.APPROVED
        elif score >= 70:
            status = SkillStatus.TESTING
        else:
            status = SkillStatus.DRAFT

        # 更新文档
        document.status = status
        document.last_tested_at = datetime.now(UTC)

        return SkillEvaluation(
            skill_id=skill_id,
            evaluated_at=datetime.now(UTC),
            score=score,
            test_result=test_result,
            recommendations=[],
        )

    async def discover_skills(
        self,
        task_description: str,
        existing_skills: Optional[List[str]] = None,
    ) -> List[str]:
        """发现完成任务所需的技能。

        Args:
            task_description: 任务描述
            existing_skills: 已有的技能ID列表

        Returns:
            List[str]: 推荐的技能ID列表
        """
        if existing_skills is None:
            existing_skills = []

        # 获取所有可用技能
        all_skills = self.list_skills(SkillStatus.APPROVED)

        # 简单匹配: 基于关键词
        recommended = []
        keywords = set(task_description.lower().split())

        for skill_doc in all_skills:
            if skill_doc.id in existing_skills:
                continue

            # 检查技能名称和描述
            skill_text = f"{skill_doc.name} {skill_doc.description}".lower()
            skill_keywords = set(skill_text.split())

            # 计算匹配度
            match_count = len(keywords & skill_keywords)
            if match_count > 0:
                recommended.append(skill_doc.id)

        return recommended

    async def create_skill_from_description(
        self,
        skill_create: SkillCreate,
    ) -> SkillDocument:
        """从描述创建技能。

        Args:
            skill_create: 技能创建配置

        Returns:
            SkillDocument: 创建的技能文档

        Note:
            这是一个占位实现,实际应该使用LLM生成技能代码
        """
        # 创建文档
        document = SkillDocument(
            _id=skill_create.name.lower().replace(" ", "_"),
            name=skill_create.name,
            description=skill_create.description,
            skill_type=skill_create.skill_type,
            parameters=skill_create.parameters,
            status=SkillStatus.DRAFT,
            code=skill_create.code or "",
            prompt_template=skill_create.prompt_template or "",
            dependencies=skill_create.dependencies or [],
            tags=skill_create.tags or [],
        )

        self._skill_documents[document.id] = document

        return document

    def get_execution_history(
        self,
        skill_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取执行历史。

        Args:
            skill_id: 技能ID过滤,如果为None则返回所有
            limit: 返回记录数量限制

        Returns:
            List[Dict[str, Any]]: 执行历史记录
        """
        history = self._execution_history

        if skill_id:
            history = [h for h in history if h["skill_id"] == skill_id]

        return history[-limit:]


# 全局管理器实例
_global_manager: Optional[SkillManager] = None


def get_skill_manager() -> SkillManager:
    """获取全局技能管理器。

    Returns:
        SkillManager: 技能管理器
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = SkillManager()
    return _global_manager


def set_skill_manager(manager: SkillManager) -> None:
    """设置全局技能管理器。

    Args:
        manager: 技能管理器
    """
    global _global_manager
    _global_manager = manager
