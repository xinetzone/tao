"""多智能体系统使用示例。

展示如何使用多智能体系统。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from taolib.testing.multi_agent import (
    # Agents
    AgentFactory,
    MainAgent,
    get_agent_factory,
    # Skills
    SkillManager,
    TextSummarizationSkill,
    CodeGenerationSkill,
    get_preset_skills,
    get_skill_manager,
    # Models
    AgentCreate,
    AgentType,
    AgentCapability,
    LoadBalanceConfig,
    LoadBalanceStrategy,
    # LLM
    LLMManager,
)


async def example_1_basic_skill_usage():
    """示例1: 基本技能使用。"""
    print("\n" + "=" * 60)
    print("示例 1: 基本技能使用")
    print("=" * 60)

    # 获取技能管理器
    skill_manager = get_skill_manager()

    # 注册预设技能
    for skill in get_preset_skills():
        print(f"  注册技能: {skill.name} ({skill.id})")
        skill_manager.register_skill(skill)

    # 列出所有技能
    print("\n  可用技能:")
    skills = skill_manager.list_skills()
    for skill in skills:
        print(f"  - {skill.name}: {skill.description}")

    # 执行文本摘要技能
    print("\n  执行文本摘要技能:")
    long_text = "这是一段很长的文本。" * 20
    try:
        result = await skill_manager.execute_skill(
            "text_summarization",
            {"text": long_text, "max_length": 50}
        )
        print(f"  摘要结果: {result}")
    except Exception as e:
        print(f"  执行失败: {e}")

    # 执行代码生成技能
    print("\n  执行代码生成技能:")
    try:
        result = await skill_manager.execute_skill(
            "code_generation",
            {"requirement": "写一个hello world函数", "language": "python"}
        )
        print(f"  生成结果: {result}")
    except Exception as e:
        print(f"  执行失败: {e}")


async def example_2_agent_creation():
    """示例2: 创建智能体。"""
    print("\n" + "=" * 60)
    print("示例 2: 创建智能体")
    print("=" * 60)

    # 获取智能体工厂
    factory = get_agent_factory()

    # 列出所有模板
    print("\n  可用智能体模板:")
    from taolib.testing.multi_agent.agents import get_all_templates
    templates = get_all_templates()
    for template in templates:
        print(f"  - {template.name}: {template.description}")

    # 从模板创建智能体
    print("\n  从模板创建代码助手智能体:")
    agent = await factory.create_agent_from_template("code_assistant", "我的代码助手")
    print(f"  智能体名称: {agent.name}")
    print(f"  智能体ID: {agent.id}")
    print(f"  智能体状态: {agent.status}")

    # 创建自定义智能体
    print("\n  创建自定义智能体:")
    agent_create = AgentCreate(
        name="自定义助手",
        description="这是一个自定义智能体",
        agent_type=AgentType.SUB,
        capabilities=[
            AgentCapability(name="问答", description="回答问题"),
            AgentCapability(name="分析", description="分析数据"),
        ],
        tags=["自定义", "助手"],
    )
    custom_agent = await factory.create_agent(agent_create)
    print(f"  智能体名称: {custom_agent.name}")
    print(f"  智能体状态: {custom_agent.status}")


async def example_3_main_agent():
    """示例3: 使用主智能体。"""
    print("\n" + "=" * 60)
    print("示例 3: 使用主智能体")
    print("=" * 60)

    # 获取智能体工厂
    factory = get_agent_factory()

    # 创建主智能体
    print("\n  创建主智能体:")
    main_agent = await factory.create_main_agent("系统主智能体")
    print(f"  主智能体名称: {main_agent.name}")
    print(f"  主智能体状态: {main_agent.status}")
    print(f"  子智能体数量: {len(main_agent._sub_agents)}")

    # 关闭主智能体
    print("\n  关闭主智能体...")
    await main_agent.shutdown()
    print("  主智能体已关闭")


async def example_4_llm_manager():
    """示例4: LLM管理器。"""
    print("\n" + "=" * 60)
    print("示例 4: LLM管理器")
    print("=" * 60)

    # 创建LLM管理器
    load_balance_config = LoadBalanceConfig(
        strategy=LoadBalanceStrategy.ROUND_ROBIN,
    )
    llm_manager = LLMManager(load_balance_config)

    # 添加模型配置
    print("\n  添加Ollama模型配置:")
    from taolib.testing.multi_agent.models import ModelConfig, ModelProvider
    model_config = ModelConfig(
        provider=ModelProvider.OLLAMA,
        model_name="llama2",
        base_url="http://localhost:11434",
        weight=1.0,
    )
    instance_id = llm_manager.add_model(model_config, "ollama-llama2")
    print(f"  模型实例ID: {instance_id}")

    # 列出可用模型
    print("\n  可用模型:")
    available_models = llm_manager.get_available_models()
    for model_id in available_models:
        print(f"  - {model_id}")


async def main():
    """主函数。"""
    print("多智能体系统 - 使用示例")
    print("=" * 60)

    try:
        await example_1_basic_skill_usage()
        await example_2_agent_creation()
        await example_3_main_agent()
        await example_4_llm_manager()

        print("\n" + "=" * 60)
        print("所有示例执行完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
