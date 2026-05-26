"""多智能体系统 - 技能模块。

包含技能协议、注册表、管理器和预设技能。
"""

from taolib.testing.multi_agent.skills.manager import (
    SkillManager,
    get_skill_manager,
    set_skill_manager,
)
from taolib.testing.multi_agent.skills.preset import (
    CodeGenerationSkill,
    DataAnalysisSkill,
    TextSummarizationSkill,
    TranslationSkill,
    get_preset_skills,
)
from taolib.testing.multi_agent.skills.protocols import (
    BaseSkill,
    Skill,
    SkillExecutionContext,
)
from taolib.testing.multi_agent.skills.registry import (
    SkillRegistry,
    get_skill_registry,
    set_skill_registry,
)

__all__ = [
    # Protocols
    "Skill",
    "BaseSkill",
    "SkillExecutionContext",
    # Registry
    "SkillRegistry",
    "get_skill_registry",
    "set_skill_registry",
    # Manager
    "SkillManager",
    "get_skill_manager",
    "set_skill_manager",
    # Preset Skills
    "TextSummarizationSkill",
    "CodeGenerationSkill",
    "TranslationSkill",
    "DataAnalysisSkill",
    "get_preset_skills",
]
