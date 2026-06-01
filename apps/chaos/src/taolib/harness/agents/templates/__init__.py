"""Agent 模板集合 - 预置可复用的 Agent 图结构模板与工厂方法。

本模块通过 :class:`AgentTemplate` 枚举对外暴露内置模板的标识，
并提供 :func:`create_from_template` 作为统一的工厂入口。

示例::

    from taolib.harness.agents.templates import AgentTemplate, create_from_template

    agent = create_from_template(
        AgentTemplate.REACT,
        config={"name": "my-react", "version": "0.1.0"},
    )
    result = agent.invoke({"query": "hello"})

新模板可通过 :func:`register_template` 注入到全局表中，便于业务侧扩展。
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import StrEnum
from typing import Any

from ..graph_agent import AgentConfig, GraphAgent, GraphSpec, NodeFn, ReActAgent

__all__ = [
    "AgentTemplate",
    "PlanAndExecuteAgent",
    "RouterAgent",
    "create_from_template",
    "register_template",
]


class AgentTemplate(StrEnum):
    """预置 Agent 模板枚举。"""

    REACT = "react"
    PLAN_AND_EXECUTE = "plan_and_execute"
    ROUTER = "router"


class PlanAndExecuteAgent(ReActAgent):
    """计划-执行模式 Agent 模板。

    在 ReAct 基础上引入显式的 ``plan`` 阶段：先生成多步计划，再按计划逐步执行
    与观察。本占位实现复用 ReAct 的循环骨架，子类可重写 :meth:`reason` 注入
    实际的计划生成逻辑。
    """

    async def reason(self, state: dict[str, Any]) -> dict[str, Any]:
        """以"先计划再推理"的方式产出下一步意图。"""
        plan = list(state.get("_plan") or [])
        if not plan:
            plan = ["analyze", "execute", "verify"]
        cursor = int(state.get("_plan_cursor", 0))
        if cursor >= len(plan):
            return {"_done": True, "_phase": "plan_complete"}
        return {
            "_plan": plan,
            "_plan_cursor": cursor + 1,
            "_current_step": plan[cursor],
            "_phase": "plan",
        }


class RouterAgent(GraphAgent):
    """路由模式 Agent 模板。

    将输入分类后转发给对应的子 Agent / 工具。本基础实现提供单层 router → handler
    的图骨架，``routes`` 通过 :class:`AgentConfig.extra` 字段（``routes`` 键）配置::

        AgentConfig(name="router", extra={"routes": {"qa": qa_node, "search": search_node}})
    """

    async def route(self, state: dict[str, Any]) -> dict[str, Any]:
        """计算路由键并写入 ``_route``。"""
        intent = str(state.get("intent") or state.get("input") or "default")
        return {"_route": intent, "_phase": "route"}

    async def fallback(self, state: dict[str, Any]) -> dict[str, Any]:
        """无匹配路由时的兜底节点。"""
        return {"_route": "fallback", "_phase": "fallback"}

    def build_graph(self) -> GraphSpec:  # type: ignore[override]
        routes: Mapping[str, Callable[[dict[str, Any]], Any]] = (
            self.config.model_extra.get("routes", {}) if self.config.model_extra else {}
        )
        nodes: dict[str, Any] = {
            "route": self._wrap(self.route),
            "fallback": self._wrap(self.fallback),
        }
        for key, handler in routes.items():
            nodes[f"handle_{key}"] = self._wrap(handler)
        mapping = {key: f"handle_{key}" for key in routes}
        mapping["__default__"] = "fallback"
        edges = [(f"handle_{key}", "end") for key in routes]
        edges.append(("fallback", "end"))
        return GraphSpec(
            nodes=nodes,
            edges=edges,
            conditional_edges=[
                (
                    "route",
                    lambda s: (
                        str(s.get("_route", "__default__"))
                        if s.get("_route") in routes
                        else "__default__"
                    ),
                    mapping,
                ),
            ],
            entry_point="route",
            finish_points=("end",),
        )

    @staticmethod
    def _wrap(handler: Callable[[dict[str, Any]], Any]) -> NodeFn:
        import inspect

        async def _node(state: dict[str, Any]) -> dict[str, Any]:
            result = handler(state)
            if inspect.isawaitable(result):
                result = await result
            return dict(result) if isinstance(result, Mapping) else {"result": result}

        return _node


# ---------------------------------------------------------------------------
# 模板注册表
# ---------------------------------------------------------------------------
type _TemplateFactory = Callable[[AgentConfig | Mapping[str, Any]], GraphAgent]

_TEMPLATES: dict[AgentTemplate, type[GraphAgent]] = {
    AgentTemplate.REACT: ReActAgent,
    AgentTemplate.PLAN_AND_EXECUTE: PlanAndExecuteAgent,
    AgentTemplate.ROUTER: RouterAgent,
}


def register_template(
    template: AgentTemplate | str, agent_cls: type[GraphAgent]
) -> None:
    """注册一个新的 Agent 模板（或覆盖已有模板）。"""
    key = AgentTemplate(template) if isinstance(template, str) else template
    _TEMPLATES[key] = agent_cls


def create_from_template(
    template: AgentTemplate | str,
    config: AgentConfig | Mapping[str, Any],
    /,
    **kwargs: Any,
) -> GraphAgent:
    """根据模板枚举构造 Agent 实例。

    Args:
        template: 模板枚举或其字符串值。
        config: Agent 配置（``AgentConfig`` 或可被其校验的字典）。
        **kwargs: 透传给具体 Agent 构造函数的额外参数（如 ``registry``、
            ``checkpointer``、``auto_register`` 等）。

    Raises:
        KeyError: 当模板未注册时抛出。
    """
    key = AgentTemplate(template) if isinstance(template, str) else template
    try:
        cls = _TEMPLATES[key]
    except KeyError as exc:  # pragma: no cover - 枚举范围有限
        raise KeyError(f"未注册的 Agent 模板: {template!r}") from exc
    return cls(config, **kwargs)
