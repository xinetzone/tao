"""预设技能。

提供常用的预设技能实现。
"""

from typing import Any

from taolib.testing.multi_agent.models import SkillParameter, SkillType
from taolib.testing.multi_agent.skills.protocols import BaseSkill, SkillExecutionContext


class TextSummarizationSkill(BaseSkill):
    """文本摘要技能。"""

    def __init__(self):
        """初始化文本摘要技能。"""
        super().__init__(
            skill_id="text_summarization",
            name="文本摘要",
            description="将长文本压缩成简洁的摘要",
            parameters=[
                SkillParameter(
                    name="text",
                    type="string",
                    description="要摘要的文本",
                    required=True,
                ),
                SkillParameter(
                    name="max_length",
                    type="number",
                    description="摘要的最大长度(字符数)",
                    required=False,
                    default=200,
                ),
            ],
        )

    async def execute(self, context: SkillExecutionContext) -> Any:
        """执行文本摘要。

        Args:
            context: 执行上下文

        Returns:
            Any: 摘要结果
        """
        text = context.parameters["text"]
        max_length = context.parameters.get("max_length", 200)

        if context.llm_provider:
            prompt = f"请将以下文本摘要成最多{max_length}个字符:\n\n{text}"
            return await context.llm_provider.generate(prompt)
        else:
            # 简单回退: 截取前max_length个字符
            if len(text) <= max_length:
                return text
            return text[:max_length] + "..."


class CodeGenerationSkill(BaseSkill):
    """代码生成技能。"""

    def __init__(self):
        """初始化代码生成技能。"""
        super().__init__(
            skill_id="code_generation",
            name="代码生成",
            description="根据需求生成代码",
            parameters=[
                SkillParameter(
                    name="requirement",
                    type="string",
                    description="代码需求描述",
                    required=True,
                ),
                SkillParameter(
                    name="language",
                    type="string",
                    description="编程语言",
                    required=False,
                    default="python",
                ),
            ],
        )

    async def execute(self, context: SkillExecutionContext) -> Any:
        """执行代码生成。

        Args:
            context: 执行上下文

        Returns:
            Any: 生成的代码
        """
        requirement = context.parameters["requirement"]
        language = context.parameters.get("language", "python")

        if context.llm_provider:
            prompt = f"请用{language}语言编写代码，满足以下需求:\n\n{requirement}"
            return await context.llm_provider.generate(prompt)
        else:
            return f"# {language}代码生成\n# 需求: {requirement}\n# (需要LLM支持)"


class TranslationSkill(BaseSkill):
    """翻译技能。"""

    def __init__(self):
        """初始化翻译技能。"""
        super().__init__(
            skill_id="translation",
            name="文本翻译",
            description="将文本从一种语言翻译成另一种语言",
            parameters=[
                SkillParameter(
                    name="text",
                    type="string",
                    description="要翻译的文本",
                    required=True,
                ),
                SkillParameter(
                    name="target_language",
                    type="string",
                    description="目标语言",
                    required=False,
                    default="中文",
                ),
                SkillParameter(
                    name="source_language",
                    type="string",
                    description="源语言(可选,自动检测)",
                    required=False,
                ),
            ],
        )

    async def execute(self, context: SkillExecutionContext) -> Any:
        """执行翻译。

        Args:
            context: 执行上下文

        Returns:
            Any: 翻译结果
        """
        text = context.parameters["text"]
        target_lang = context.parameters.get("target_language", "中文")
        source_lang = context.parameters.get("source_language")

        if context.llm_provider:
            if source_lang:
                prompt = f"请将以下{source_lang}文本翻译成{target_lang}:\n\n{text}"
            else:
                prompt = f"请将以下文本翻译成{target_lang}:\n\n{text}"
            return await context.llm_provider.generate(prompt)
        else:
            return f"[翻译结果] {text} (需要LLM支持)"


class DataAnalysisSkill(BaseSkill):
    """数据分析技能。"""

    def __init__(self):
        """初始化数据分析技能。"""
        super().__init__(
            skill_id="data_analysis",
            name="数据分析",
            description="对数据进行简单的统计分析",
            parameters=[
                SkillParameter(
                    name="data",
                    type="string",
                    description="数据(CSV格式或JSON)",
                    required=True,
                ),
                SkillParameter(
                    name="analysis_type",
                    type="string",
                    description="分析类型: summary, statistics, visualization",
                    required=False,
                    default="summary",
                ),
            ],
        )

    async def execute(self, context: SkillExecutionContext) -> Any:
        """执行数据分析。

        Args:
            context: 执行上下文

        Returns:
            Any: 分析结果
        """
        data = context.parameters["data"]
        analysis_type = context.parameters.get("analysis_type", "summary")

        if context.llm_provider:
            prompt = f"请对以下数据进行{analysis_type}分析:\n\n{data}"
            return await context.llm_provider.generate(prompt)
        else:
            return f"[数据分析] 类型: {analysis_type}\n数据长度: {len(data)}字符\n(需要LLM支持)"


def get_preset_skills() -> list[BaseSkill]:
    """获取所有预设技能。

    Returns:
        list[BaseSkill]: 预设技能列表
    """
    return [
        TextSummarizationSkill(),
        CodeGenerationSkill(),
        TranslationSkill(),
        DataAnalysisSkill(),
    ]
