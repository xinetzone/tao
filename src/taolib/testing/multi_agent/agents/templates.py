"""预设智能体模板。

提供常用的智能体模板,方便快速创建专用子智能体。
"""

from taolib.testing.multi_agent.models import (
    AgentCapability,
    AgentConfig,
    AgentTemplate,
    AgentType,
)


def get_code_assistant_template() -> AgentTemplate:
    """获取代码助手智能体模板。"""
    return AgentTemplate(
        id="code_assistant",
        name="代码助手",
        description="专业的代码编写、调试和优化助手",
        agent_type=AgentType.SPECIALIZED,
        capabilities=[
            AgentCapability(
                name="代码生成",
                description="根据需求生成高质量代码",
                confidence=0.9,
                tags=["coding", "generation", "python", "javascript"],
            ),
            AgentCapability(
                name="代码审查",
                description="审查代码质量,发现潜在问题",
                confidence=0.85,
                tags=["review", "quality", "bug-detection"],
            ),
            AgentCapability(
                name="调试协助",
                description="帮助定位和解决代码bug",
                confidence=0.88,
                tags=["debugging", "troubleshooting"],
            ),
            AgentCapability(
                name="代码优化",
                description="优化代码性能和可读性",
                confidence=0.82,
                tags=["optimization", "performance", "refactoring"],
            ),
        ],
        config=AgentConfig(
            max_concurrent_tasks=2,
            timeout_seconds=600,
            system_prompt="""你是一个专业的代码助手。你的职责是:
1. 编写清晰、高效、可维护的代码
2. 遵循最佳实践和设计模式
3. 提供详细的代码解释和注释
4. 帮助用户理解和学习编程概念

请始终提供完整、可运行的代码示例。""",
            temperature=0.6,
        ),
        skills=[],
        tags=["coding", "programming", "development"],
    )


def get_writing_assistant_template() -> AgentTemplate:
    """获取写作助手智能体模板。"""
    return AgentTemplate(
        id="writing_assistant",
        name="写作助手",
        description="专业的文章写作、编辑和润色助手",
        agent_type=AgentType.SPECIALIZED,
        capabilities=[
            AgentCapability(
                name="文章写作",
                description="撰写各种类型的文章和文档",
                confidence=0.92,
                tags=["writing", "content", "articles"],
            ),
            AgentCapability(
                name="文本润色",
                description="改进文本的表达和流畅度",
                confidence=0.88,
                tags=["editing", "polishing", "style"],
            ),
            AgentCapability(
                name="翻译",
                description="多语言文本翻译",
                confidence=0.85,
                tags=["translation", "languages"],
            ),
            AgentCapability(
                name="摘要生成",
                description="生成文章摘要和总结",
                confidence=0.90,
                tags=["summarization", "summary"],
            ),
        ],
        config=AgentConfig(
            max_concurrent_tasks=3,
            timeout_seconds=900,
            system_prompt="""你是一个专业的写作助手。你的职责是:
1. 创作清晰、引人入胜的内容
2. 根据目标受众调整写作风格
3. 确保语法正确、表达流畅
4. 尊重原创性和知识产权

请始终提供高质量的文本输出。""",
            temperature=0.8,
        ),
        skills=[],
        tags=["writing", "content", "communication"],
    )


def get_data_analyst_template() -> AgentTemplate:
    """获取数据分析智能体模板。"""
    return AgentTemplate(
        id="data_analyst",
        name="数据分析",
        description="专业的数据处理、分析和可视化助手",
        agent_type=AgentType.SPECIALIZED,
        capabilities=[
            AgentCapability(
                name="数据清洗",
                description="清洗和预处理原始数据",
                confidence=0.85,
                tags=["data-cleaning", "preprocessing"],
            ),
            AgentCapability(
                name="统计分析",
                description="进行统计分析和假设检验",
                confidence=0.88,
                tags=["statistics", "analysis", "hypothesis-testing"],
            ),
            AgentCapability(
                name="数据可视化",
                description="创建清晰的数据图表和可视化",
                confidence=0.86,
                tags=["visualization", "charts", "plots"],
            ),
            AgentCapability(
                name="洞察生成",
                description="从数据中提取有价值的洞察",
                confidence=0.82,
                tags=["insights", "business-intelligence"],
            ),
        ],
        config=AgentConfig(
            max_concurrent_tasks=2,
            timeout_seconds=1200,
            system_prompt="""你是一个专业的数据分析助手。你的职责是:
1. 使用科学的方法分析数据
2. 生成清晰、准确的可视化图表
3. 提供可操作的数据洞察
4. 确保分析结果的可重复性

请使用Python和常用的数据科学库进行分析。""",
            temperature=0.5,
        ),
        skills=[],
        tags=["data", "analysis", "statistics", "visualization"],
    )


def get_research_assistant_template() -> AgentTemplate:
    """获取研究助手智能体模板。"""
    return AgentTemplate(
        id="research_assistant",
        name="研究助手",
        description="专业的文献调研、信息收集和学术写作助手",
        agent_type=AgentType.SPECIALIZED,
        capabilities=[
            AgentCapability(
                name="文献调研",
                description="收集和整理相关文献资料",
                confidence=0.82,
                tags=["research", "literature", "survey"],
            ),
            AgentCapability(
                name="信息综合",
                description="综合分析多源信息",
                confidence=0.85,
                tags=["synthesis", "information-integration"],
            ),
            AgentCapability(
                name="学术写作",
                description="撰写学术论文和报告",
                confidence=0.88,
                tags=["academic", "writing", "papers"],
            ),
            AgentCapability(
                name="引用管理",
                description="管理参考文献和引用格式",
                confidence=0.90,
                tags=["citations", "references", "bibliography"],
            ),
        ],
        config=AgentConfig(
            max_concurrent_tasks=2,
            timeout_seconds=1800,
            system_prompt="""你是一个专业的研究助手。你的职责是:
1. 进行全面的文献调研
2. 确保信息来源的可靠性
3. 遵循学术诚信和规范
4. 提供准确的引用和参考

请始终注明信息来源和引用。""",
            temperature=0.6,
        ),
        skills=[],
        tags=["research", "academic", "literature"],
    )


def get_general_assistant_template() -> AgentTemplate:
    """获取通用助手智能体模板。"""
    return AgentTemplate(
        id="general_assistant",
        name="通用助手",
        description="全能型智能助手,可处理各种类型的任务",
        agent_type=AgentType.SUB,
        capabilities=[
            AgentCapability(
                name="问答",
                description="回答各种问题",
                confidence=0.90,
                tags=["qa", "questions", "answers"],
            ),
            AgentCapability(
                name="信息检索",
                description="查找和整理信息",
                confidence=0.85,
                tags=["search", "information", "retrieval"],
            ),
            AgentCapability(
                name="创意生成",
                description="生成创意和想法",
                confidence=0.88,
                tags=["creative", "ideas", "brainstorming"],
            ),
            AgentCapability(
                name="问题解决",
                description="帮助解决各种问题",
                confidence=0.82,
                tags=["problem-solving", "troubleshooting"],
            ),
        ],
        config=AgentConfig(
            max_concurrent_tasks=5,
            timeout_seconds=300,
            system_prompt="""你是一个友好、乐于助人的通用助手。你的职责是:
1. 尽力帮助用户解决问题
2. 保持友好和专业的态度
3. 承认自己的局限性
4. 提供有用和安全的建议

请始终以用户的最佳利益为重。""",
            temperature=0.7,
        ),
        skills=[],
        tags=["general", "assistant", "helpful"],
    )


def get_template(template_id: str) -> AgentTemplate | None:
    """根据ID获取模板。

    Args:
        template_id: 模板ID

    Returns:
        AgentTemplate | None: 模板实例,如果不存在则返回None
    """
    template_getters = {
        "code_assistant": get_code_assistant_template,
        "writing_assistant": get_writing_assistant_template,
        "data_analyst": get_data_analyst_template,
        "research_assistant": get_research_assistant_template,
        "general_assistant": get_general_assistant_template,
    }

    getter = template_getters.get(template_id)
    if getter:
        return getter()
    return None


def get_all_templates() -> list[AgentTemplate]:
    """获取所有预设模板。"""
    return [
        get_code_assistant_template(),
        get_writing_assistant_template(),
        get_data_analyst_template(),
        get_research_assistant_template(),
        get_general_assistant_template(),
    ]


__all__ = [
    "AgentTemplate",
    "get_code_assistant_template",
    "get_writing_assistant_template",
    "get_data_analyst_template",
    "get_research_assistant_template",
    "get_general_assistant_template",
    "get_template",
    "get_all_templates",
]

