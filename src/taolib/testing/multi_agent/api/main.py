"""多智能体系统 API。

提供RESTful API接口。
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from taolib.testing.multi_agent.agents import (
    AgentFactory,
    get_agent_factory,
    get_all_templates,
)
from taolib.testing.multi_agent.skills import get_preset_skills
from taolib.testing.multi_agent.llm import LLMManager, LoadBalanceConfig, LoadBalanceStrategy
from taolib.testing.multi_agent.models import (
    AgentCreate,
    AgentResponse,
    TaskCreate,
    TaskResponse,
)
from taolib.testing.multi_agent.skills import get_skill_manager


# 全局管理器
llm_manager: LLMManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器。"""
    # 启动时初始化
    global llm_manager
    load_balance_config = LoadBalanceConfig(strategy=LoadBalanceStrategy.ROUND_ROBIN)
    llm_manager = LLMManager(load_balance_config)

    # 初始化技能管理器
    skill_manager = get_skill_manager()

    # 注册预设技能
    for skill in get_preset_skills():
        skill_manager.register_skill(skill)

    yield

    # 关闭时清理
    pass


app = FastAPI(
    title="多智能体系统 API",
    description="无需API KEY的免费大模型多智能体系统",
    version="0.1.0",
    lifespan=lifespan,
)


# 请求模型
class ExecuteSkillRequest(BaseModel):
    """执行技能请求。"""

    skill_id: str
    parameters: dict[str, Any]


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查。"""
    return {"status": "healthy"}


# 智能体API
@app.post("/agents", response_model=AgentResponse)
async def create_agent(agent_create: AgentCreate):
    """创建智能体。"""
    factory = get_agent_factory()
    agent = await factory.create_agent(agent_create)
    return agent.document.to_response()


@app.get("/agents/templates")
async def list_agent_templates():
    """列出智能体模板。"""
    from taolib.testing.multi_agent.agents import get_all_templates

    templates = get_all_templates()
    return [
        {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "agent_type": template.agent_type,
        }
        for template in templates
    ]


# 技能API
@app.get("/skills")
async def list_skills():
    """列出所有技能。"""
    manager = get_skill_manager()
    skills = manager.list_skills()
    return [
        {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "status": skill.status,
        }
        for skill in skills
    ]


@app.post("/skills/execute")
async def execute_skill(request: ExecuteSkillRequest):
    """执行技能。"""
    manager = get_skill_manager()
    try:
        result = await manager.execute_skill(request.skill_id, request.parameters)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 任务API
@app.post("/tasks", response_model=TaskResponse)
async def create_task(task_create: TaskCreate):
    """创建任务。"""
    # 这里简化处理,实际应该使用主智能体
    from taolib.testing.multi_agent.models import TaskDocument
    import uuid

    task_doc = TaskDocument(
        _id=str(uuid.uuid4()),
        **task_create.model_dump(),
    )
    return task_doc.to_response()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
