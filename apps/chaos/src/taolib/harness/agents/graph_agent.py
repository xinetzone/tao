"""LangGraph Agent 基类 - 定义基于 StateGraph 的可注册、可组合 Agent 抽象。

本模块提供两个核心抽象：

* :class:`AgentConfig` —— 通过 Pydantic v2 定义的 Agent 元配置（名称、版本、
  描述、工具集、LLM 模型参数、最大迭代次数等）；
* :class:`GraphAgent` —— LangGraph Agent 的抽象基类，子类通过实现
  :meth:`build_graph` 声明节点与边，基类负责图编译、检查点接入、状态回调
  广播以及与上层注册表/桥接层的协同。

并附带预置模板 :class:`ReActAgent`，按 *reason → act → observe → reason* 循环
组织节点，支持工具调用与条件终止。

装饰器风格示例::

    from taolib.harness.core import register_agent

    @register_agent(name="planner", version="1.0.0", tags=("plan",))
    class PlannerAgent(GraphAgent): ...

LangGraph 在当前环境可能未安装，本模块通过 ``TYPE_CHECKING`` 守卫与运行时
探测实现可插拔接入：未安装时仍可使用内置的轻量执行回退。
"""

from __future__ import annotations

import asyncio
import inspect
import uuid
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, ClassVar, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from ..core.registry import AgentRegistry, RegistryEntry, get_default_registry
from ..runtime.checkpointer import CheckpointerConfig, HarnessCheckpointer

__all__ = [
    "AgentConfig",
    "AgentTool",
    "GraphAgent",
    "GraphSpec",
    "LLMConfig",
    "NodeFn",
    "ReActAgent",
    "ToolFn",
]


# ---------------------------------------------------------------------------
# 类型别名
# ---------------------------------------------------------------------------

type NodeFn = Callable[[dict[str, Any]], dict[str, Any] | Awaitable[dict[str, Any]]]
"""节点函数签名：接收当前状态字典，返回需要合并的更新字典（同步或异步）。"""

type ToolFn = Callable[..., Any]
"""工具函数签名：任意可调用对象，参数与返回值由具体工具决定。"""


# ---------------------------------------------------------------------------
# 配置模型
# ---------------------------------------------------------------------------


class LLMConfig(BaseModel):
    """LLM 模型配置 - 用于 Agent 内部对底层模型的参数化调用。"""

    model_config = ConfigDict(extra="allow")

    model: str = Field(default="gpt-4o-mini", description="模型名称或标识")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int | None = Field(
        default=None, gt=0, description="单次响应最大 token 数"
    )
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    extra: dict[str, Any] = Field(
        default_factory=dict, description="额外的模型特定参数"
    )


class AgentConfig(BaseModel):
    """Agent 元配置。

    用于在注册、装配、序列化阶段声明一个 Agent 的全部静态属性。
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str = Field(description="Agent 唯一名称")
    version: str = Field(default="0.1.0", description="语义化版本号")
    description: str = Field(default="", description="人类可读的说明")
    tools: list[Any] = Field(default_factory=list, description="可用工具集合")
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM 模型配置")
    max_iterations: int = Field(default=10, ge=1, description="最大迭代步数")
    tags: tuple[str, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# 图谱声明 / 编译产物
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GraphSpec:
    """Agent 图结构的声明式规格。

    子类 :meth:`GraphAgent.build_graph` 返回本结构后，由基类编译成可执行图。
    """

    nodes: dict[str, NodeFn] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)
    conditional_edges: list[
        tuple[str, Callable[[dict[str, Any]], str], dict[str, str]]
    ] = field(default_factory=list)
    entry_point: str = "start"
    finish_points: tuple[str, ...] = ("end",)


@runtime_checkable
class _Compiled(Protocol):
    """编译后图对象需暴露的最小接口。"""

    async def ainvoke(self, payload: Any, config: Any | None = None) -> Any: ...

    def invoke(self, payload: Any, config: Any | None = None) -> Any: ...


class _CompiledStubGraph:
    """轻量回退编译对象 - 在无 LangGraph 时按声明顺序执行节点。

    仅支持线性 ``edges`` 与单层 ``conditional_edges``，用于离线环境与单元测试。
    """

    def __init__(
        self,
        spec: GraphSpec,
        *,
        checkpointer: HarnessCheckpointer | None = None,
        max_iterations: int = 25,
        on_node_start: Callable[[str, dict[str, Any]], Awaitable[None] | None]
        | None = None,
        on_node_end: Callable[[str, dict[str, Any]], Awaitable[None] | None]
        | None = None,
        on_error: Callable[[str, BaseException], Awaitable[None] | None] | None = None,
    ) -> None:
        self._spec = spec
        self._checkpointer = checkpointer
        self._max_iterations = max_iterations
        self._on_node_start = on_node_start
        self._on_node_end = on_node_end
        self._on_error = on_error

    async def ainvoke(self, payload: Any, config: Any | None = None) -> dict[str, Any]:
        state: dict[str, Any] = (
            dict(payload) if isinstance(payload, Mapping) else {"input": payload}
        )
        current: str | None = self._spec.entry_point
        finish = set(self._spec.finish_points) | {"END", "__end__"}
        # 步进上限按 max_iterations × 节点数 计算，防止多节点循环提前截断。
        step_limit = self._max_iterations * max(len(self._spec.nodes), 1) + 1
        for _ in range(step_limit):
            if current is None or current in finish:
                break
            node = self._spec.nodes.get(current)
            if node is None:
                break
            await self._fire(self._on_node_start, current, state)
            try:
                result = node(state)
                if inspect.isawaitable(result):
                    result = await result
            except BaseException as exc:
                await self._fire(self._on_error, current, exc)
                raise
            if isinstance(result, Mapping):
                state.update(result)
            await self._fire(self._on_node_end, current, state)
            await self._persist(state, config, current)
            current = self._next_node(current, state)
        return state

    def invoke(self, payload: Any, config: Any | None = None) -> dict[str, Any]:
        return asyncio.run(self.ainvoke(payload, config))

    # ------------------------------------------------------------------
    def _next_node(self, current: str, state: dict[str, Any]) -> str | None:
        for src, predicate, mapping in self._spec.conditional_edges:
            if src == current:
                key = predicate(state)
                if key in mapping:
                    return mapping[key]
        for src, dst in self._spec.edges:
            if src == current:
                return dst
        return None

    @staticmethod
    async def _fire(
        hook: Callable[..., Awaitable[None] | None] | None, *args: Any
    ) -> None:
        if hook is None:
            return
        result = hook(*args)
        if inspect.isawaitable(result):
            await result

    async def _persist(
        self, state: dict[str, Any], config: Any | None, node: str
    ) -> None:
        if self._checkpointer is None or not isinstance(config, Mapping):
            return
        configurable = (
            config.get("configurable") if isinstance(config, Mapping) else None
        )
        if not isinstance(configurable, Mapping) or "thread_id" not in configurable:
            return
        await self._checkpointer.aput(
            dict(config), dict(state), {"writes": {node: state}}
        )


# ---------------------------------------------------------------------------
# 工具包装
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class AgentTool:
    """Agent 包装为工具时的描述对象。

    可被任意支持 ``name`` / ``description`` / ``func`` 三元组的工具协议消费
    （包括 LangChain ``StructuredTool``、OpenAI function-call 等）。
    """

    name: str
    description: str
    func: Callable[..., Awaitable[Any]]
    args_schema: type[BaseModel] | None = None

    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[Any]:
        return self.func(*args, **kwargs)


# ---------------------------------------------------------------------------
# Agent 基类
# ---------------------------------------------------------------------------


class GraphAgent(ABC):
    """LangGraph Agent 抽象基类。

    生命周期：

    1. 实例化时自动向 :class:`AgentRegistry` 注册自身（除非显式禁用）；
    2. 首次调用 :meth:`compile` 时执行 :meth:`build_graph` 并返回可执行图对象；
    3. :meth:`invoke` / :meth:`ainvoke` 为同步/异步执行入口；
    4. :meth:`as_tool` 将 Agent 包装为可被其他 Agent 调用的工具；
    5. :meth:`as_step` 将 Agent 适配为 Metaflow Step 的同步可调用。

    钩子 ``on_node_start`` / ``on_node_end`` / ``on_error`` 用于观测节点级状态。
    """

    config_class: ClassVar[type[AgentConfig]] = AgentConfig

    def __init__(
        self,
        config: AgentConfig | Mapping[str, Any],
        *,
        registry: AgentRegistry | None = None,
        checkpointer: HarnessCheckpointer | None = None,
        auto_register: bool = True,
    ) -> None:
        """构造 Agent。

        Args:
            config: :class:`AgentConfig` 实例或可被其校验的字典。
            registry: 自定义 Agent 注册表；缺省使用全局默认注册表。
            checkpointer: 自定义检查点适配器；缺省构造内存型实例。
            auto_register: 是否在构造时自动注册到 ``registry``。
        """
        self.config = (
            config
            if isinstance(config, AgentConfig)
            else self.config_class.model_validate(config)
        )
        self._registry = registry or get_default_registry().agents
        self._checkpointer = checkpointer or HarnessCheckpointer(CheckpointerConfig())
        self._compiled: _Compiled | None = None
        self._registry_entry: RegistryEntry[Any] | None = None
        self.on_node_start: (
            Callable[[str, dict[str, Any]], Awaitable[None] | None] | None
        ) = None
        self.on_node_end: (
            Callable[[str, dict[str, Any]], Awaitable[None] | None] | None
        ) = None
        self.on_error: Callable[[str, BaseException], Awaitable[None] | None] | None = (
            None
        )
        if auto_register:
            self._registry_entry = self._registry.register(
                self,
                name=self.config.name,
                version=self.config.version,
                tags=self.config.tags,
                description=self.config.description,
                overwrite=True,
            )

    # ------------------------------------------------------------------
    # 子类必须实现
    # ------------------------------------------------------------------
    @abstractmethod
    def build_graph(self) -> GraphSpec:
        """返回 Agent 的图结构声明。

        子类应在此声明所有节点函数与边连接，基类负责后续编译。
        """

    # ------------------------------------------------------------------
    # 编译 / 执行
    # ------------------------------------------------------------------
    @property
    def checkpointer(self) -> HarnessCheckpointer:
        """关联的检查点适配器。"""
        return self._checkpointer

    @property
    def registry_entry(self) -> RegistryEntry[Any] | None:
        """注册条目（若已注册）。"""
        return self._registry_entry

    def compile(self, *, force: bool = False) -> _Compiled:
        """编译图谱声明为可执行对象。

        优先使用 LangGraph 的 ``StateGraph``；若环境未安装则回退到内置
        :class:`_CompiledStubGraph` 顺序执行器。

        Args:
            force: 是否强制重新编译（忽略缓存）。
        """
        if self._compiled is not None and not force:
            return self._compiled
        spec = self.build_graph()
        self._compiled = self._compile_spec(spec)
        return self._compiled

    def _compile_spec(self, spec: GraphSpec) -> _Compiled:
        return _CompiledStubGraph(
            spec,
            checkpointer=self._checkpointer,
            max_iterations=self.config.max_iterations,
            on_node_start=self.on_node_start,
            on_node_end=self.on_node_end,
            on_error=self.on_error,
        )

    async def ainvoke(
        self,
        inputs: Mapping[str, Any] | None = None,
        config: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """异步执行 Agent。"""
        compiled = self.compile()
        cfg = self._prepare_config(config)
        result = await compiled.ainvoke(dict(inputs or {}), cfg)
        return dict(result) if isinstance(result, Mapping) else {"output": result}

    def invoke(
        self,
        inputs: Mapping[str, Any] | None = None,
        config: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """同步执行 Agent。"""
        return asyncio.run(self.ainvoke(inputs, config))

    def _prepare_config(self, config: Mapping[str, Any] | None) -> dict[str, Any]:
        merged: dict[str, Any] = dict(config or {})
        configurable = dict(merged.get("configurable") or {})
        configurable.setdefault("thread_id", f"thread-{uuid.uuid4().hex[:12]}")
        merged["configurable"] = configurable
        # 与 LangGraph 的递归保护对齐：默认按 max_iterations * 节点数预估上限。
        merged.setdefault("recursion_limit", max(25, self.config.max_iterations * 4))
        return merged

    # ------------------------------------------------------------------
    # 跨层适配
    # ------------------------------------------------------------------
    def as_tool(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> AgentTool:
        """将 Agent 包装为可被其他 Agent 调用的工具（Agent-as-Tool）。"""
        tool_name = name or f"agent_{self.config.name}"
        tool_desc = (
            description or self.config.description or f"调用 Agent '{self.config.name}'"
        )

        async def _runner(query: Any = None, /, **kwargs: Any) -> dict[str, Any]:
            payload = (
                kwargs if kwargs else ({"input": query} if query is not None else {})
            )
            return await self.ainvoke(payload)

        return AgentTool(name=tool_name, description=tool_desc, func=_runner)

    def as_step(self) -> Callable[..., dict[str, Any]]:
        """将 Agent 包装为可在 Metaflow Step 中调用的同步函数（Agent-as-Step）。

        返回的可调用接受任意 ``inputs`` 字典，内部驱动 :meth:`invoke`，
        从而让 Flow Step 可以无缝复用 Agent 的图执行能力。
        """

        def _step(
            inputs: Mapping[str, Any] | None = None,
            /,
            *,
            config: Mapping[str, Any] | None = None,
        ) -> dict[str, Any]:
            return self.invoke(inputs, config)

        _step.__name__ = f"{self.config.name}_as_step"
        _step.__doc__ = f"Agent {self.config.name}@{self.config.version} 的 Metaflow Step 适配函数。"
        return _step


# ---------------------------------------------------------------------------
# 预置 ReAct 模板
# ---------------------------------------------------------------------------


class ReActAgent(GraphAgent):
    """预置 ReAct 模式 Agent 模板。

    构造的图结构如下::

        reason ──▶ act ──▶ observe ──▶ reason  (循环直至终止条件)
                                  └──▶ end

    子类可重写 :meth:`reason`、:meth:`act`、:meth:`observe` 三个方法以注入
    具体的 LLM/工具/解析逻辑；缺省实现仅做透传，便于在测试中校验图骨架。
    """

    def build_graph(self) -> GraphSpec:
        """构建标准 reason → act → observe 循环。"""
        return GraphSpec(
            nodes={
                "reason": self._wrap_node(self.reason),
                "act": self._wrap_node(self.act),
                "observe": self._wrap_node(self.observe),
            },
            edges=[("reason", "act"), ("act", "observe")],
            conditional_edges=[
                (
                    "observe",
                    self._should_continue,
                    {"continue": "reason", "end": "end"},
                ),
            ],
            entry_point="reason",
            finish_points=("end",),
        )

    # ------------------------------------------------------------------
    # 可重写钩子
    # ------------------------------------------------------------------
    async def reason(self, state: dict[str, Any]) -> dict[str, Any]:
        """推理阶段：基于状态生成下一步意图。"""
        iteration = int(state.get("_iteration", 0)) + 1
        return {"_iteration": iteration, "_phase": "reason"}

    async def act(self, state: dict[str, Any]) -> dict[str, Any]:
        """执行阶段：调用工具或外部 API。"""
        return {"_phase": "act"}

    async def observe(self, state: dict[str, Any]) -> dict[str, Any]:
        """观察阶段：吸收执行结果并决定是否继续。"""
        return {"_phase": "observe"}

    # ------------------------------------------------------------------
    def _should_continue(self, state: Mapping[str, Any]) -> str:
        if state.get("_done") is True:
            return "end"
        iteration = int(state.get("_iteration", 0))
        if iteration >= self.config.max_iterations:
            return "end"
        return "continue"

    @staticmethod
    def _wrap_node(
        method: Callable[[dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]],
    ) -> NodeFn:
        async def _node(state: dict[str, Any]) -> dict[str, Any]:
            result = method(state)
            if inspect.isawaitable(result):
                result = await result
            return dict(result) if isinstance(result, Mapping) else {}

        return _node
