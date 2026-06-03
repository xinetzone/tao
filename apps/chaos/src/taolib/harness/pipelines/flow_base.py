"""Metaflow Flow 基类 - 与 Harness 系统集成的 FlowSpec 扩展。

本模块定义两个核心抽象：

* :class:`FlowConfig` —— 通过 Pydantic v2 定义的 Flow 元配置（名称、版本、
  描述、资源要求、环境变量等）；
* :class:`HarnessFlow` —— 与 :class:`FlowRegistry` 自动集成的 Flow 基类，
  内置状态回调钩子、产物访问与状态查询方法，并提供 :meth:`as_tool` 将 Flow
  包装为 LangGraph Agent 可调用的工具（Flow-as-Tool）。

并附带预置模板 :class:`EvalFlow`：以
*start → prepare_data → run_agent → collect_metrics → report → end*
六步骨架承载评估场景；每步暴露明确的输入/输出协议，便于子类按需重写。

装饰器风格示例::

    from taolib.harness.core import register_flow

    @register_flow(name="rag-eval", version="1.0.0", tags=("eval",))
    class RagEvalFlow(EvalFlow): ...

Metaflow 在当前环境可能未安装，本模块通过 ``TYPE_CHECKING`` 守卫与运行时
探测实现可插拔接入：未安装时仍可在内存中模拟 Step 顺序执行。
"""

from __future__ import annotations

import asyncio
import inspect
import time
import uuid
from collections.abc import Awaitable, Callable, Mapping
from enum import StrEnum
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from ..core.registry import FlowRegistry, RegistryEntry, get_default_registry

if TYPE_CHECKING:  # pragma: no cover - 可选依赖
    from ..agents.graph_agent import AgentTool

__all__ = [
    "EvalFlow",
    "FlowArtifact",
    "FlowConfig",
    "FlowResources",
    "FlowStatus",
    "HarnessFlow",
    "StepFn",
    "StepResult",
]


# ---------------------------------------------------------------------------
# 类型与状态
# ---------------------------------------------------------------------------

type StepFn = Callable[[dict[str, Any]], dict[str, Any] | Awaitable[dict[str, Any]]]
"""Step 函数签名：接收当前 Flow 上下文，返回需要合并的更新字典（同步或异步）。"""


class FlowStatus(StrEnum):
    """Flow 运行状态。"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FlowResources(BaseModel):
    """Flow 资源声明 - 用于在 Metaflow ``@resources`` 装饰器中映射。"""

    model_config = ConfigDict(extra="allow")

    cpu: int = Field(default=1, ge=1)
    memory_mb: int = Field(default=512, ge=64, description="内存上限（MB）")
    gpu: int = Field(default=0, ge=0)
    disk_mb: int | None = Field(default=None, ge=64)


class FlowConfig(BaseModel):
    """Flow 元配置。"""

    model_config = ConfigDict(extra="allow")

    name: str = Field(description="Flow 唯一名称")
    version: str = Field(default="0.1.0", description="语义化版本号")
    description: str = Field(default="", description="人类可读说明")
    resources: FlowResources = Field(
        default_factory=FlowResources, description="资源要求"
    )
    env: dict[str, str] = Field(default_factory=dict, description="环境变量映射")
    tags: tuple[str, ...] = Field(default_factory=tuple)
    max_retries: int = Field(
        default=0, ge=0, description="单个 Step 失败的最大重试次数"
    )


class FlowArtifact(BaseModel):
    """Flow 产物的标准包装 - 对齐 Metaflow ``Artifact`` 概念。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str
    step: str
    value: Any = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


class StepResult(BaseModel):
    """单个 Step 执行结果。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    step: str
    status: FlowStatus = FlowStatus.SUCCEEDED
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    started_at: float = Field(default_factory=time.time)
    finished_at: float | None = None


# ---------------------------------------------------------------------------
# Flow 基类
# ---------------------------------------------------------------------------


class HarnessFlow:
    """Metaflow Flow 基类（Harness 增强版）。

    生命周期：

    1. 实例化时自动向 :class:`FlowRegistry` 注册自身（除非显式禁用）；
    2. :meth:`steps` 子类定义有序的 Step 列表（``(name, callable)`` 元组）；
    3. :meth:`run` / :meth:`arun` 同步/异步执行整个 Flow；
    4. :meth:`as_tool` 将 Flow 包装为 LangGraph Agent 可调用的工具；
    5. :meth:`get_artifacts` / :meth:`get_status` 查询执行产物与运行状态。

    钩子：``on_step_start``、``on_step_end``、``on_complete``、``on_failure``。
    """

    config_class: ClassVar[type[FlowConfig]] = FlowConfig

    def __init__(
        self,
        config: FlowConfig | Mapping[str, Any],
        *,
        registry: FlowRegistry | None = None,
        auto_register: bool = True,
    ) -> None:
        """构造 Flow。

        Args:
            config: :class:`FlowConfig` 实例或可被其校验的字典。
            registry: 自定义 Flow 注册表；缺省使用全局默认注册表。
            auto_register: 是否在构造时自动注册到 ``registry``。
        """
        self.config = (
            config
            if isinstance(config, FlowConfig)
            else self.config_class.model_validate(config)
        )
        self._registry = registry or get_default_registry().flows
        self._registry_entry: RegistryEntry[Any] | None = None
        self._artifacts: list[FlowArtifact] = []
        self._results: list[StepResult] = []
        self._status = FlowStatus.PENDING
        self._run_id: str = ""
        self.on_step_start: (
            Callable[[str, dict[str, Any]], Awaitable[None] | None] | None
        ) = None
        self.on_step_end: Callable[[StepResult], Awaitable[None] | None] | None = None
        self.on_complete: (
            Callable[[list[StepResult]], Awaitable[None] | None] | None
        ) = None
        self.on_failure: Callable[[StepResult], Awaitable[None] | None] | None = None
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
    # 子类应声明 Step 序列
    # ------------------------------------------------------------------
    def steps(self) -> list[tuple[str, StepFn]]:
        """返回 Flow 的有序 Step 列表，子类必须重写。"""
        raise NotImplementedError("子类必须实现 steps() 方法以声明 Flow 步骤")

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------
    @property
    def registry_entry(self) -> RegistryEntry[Any] | None:
        """注册条目（若已注册）。"""
        return self._registry_entry

    @property
    def run_id(self) -> str:
        """当前运行 ID。"""
        return self._run_id

    def get_status(self) -> FlowStatus:
        """查询 Flow 当前运行状态。"""
        return self._status

    def get_artifacts(self, *, step: str | None = None) -> list[FlowArtifact]:
        """获取 Flow 产出的数据卡片（可按 Step 过滤）。"""
        if step is None:
            return list(self._artifacts)
        return [a for a in self._artifacts if a.step == step]

    def emit_artifact(
        self, name: str, value: Any, *, step: str, **metadata: Any
    ) -> FlowArtifact:
        """显式记录一个 Step 产出的数据卡片。"""
        artifact = FlowArtifact(name=name, step=step, value=value, metadata=metadata)
        self._artifacts.append(artifact)
        return artifact

    # ------------------------------------------------------------------
    # 执行
    # ------------------------------------------------------------------
    async def arun(
        self,
        inputs: Mapping[str, Any] | None = None,
        *,
        run_id: str | None = None,
    ) -> list[StepResult]:
        """异步执行 Flow，返回所有 Step 的结果列表。"""
        self._run_id = run_id or f"run-{uuid.uuid4().hex[:12]}"
        self._artifacts.clear()
        self._results.clear()
        self._status = FlowStatus.RUNNING
        context: dict[str, Any] = dict(inputs or {})
        last_failure: StepResult | None = None
        for name, step in self.steps():
            result = await self._run_step(name, step, context)
            self._results.append(result)
            if result.status is FlowStatus.FAILED:
                last_failure = result
                break
            context.update(result.output)
        if last_failure is not None:
            self._status = FlowStatus.FAILED
            await self._fire(self.on_failure, last_failure)
        else:
            self._status = FlowStatus.SUCCEEDED
            await self._fire(self.on_complete, list(self._results))
        return list(self._results)

    def run(
        self,
        inputs: Mapping[str, Any] | None = None,
        *,
        run_id: str | None = None,
    ) -> list[StepResult]:
        """同步执行 Flow。"""
        return asyncio.run(self.arun(inputs, run_id=run_id))

    async def _run_step(
        self, name: str, step: StepFn, context: dict[str, Any]
    ) -> StepResult:
        await self._fire(self.on_step_start, name, context)
        started = time.time()
        attempt = 0
        last_error: BaseException | None = None
        while attempt <= self.config.max_retries:
            try:
                output = step(context)
                if inspect.isawaitable(output):
                    output = await output
                merged = (
                    dict(output) if isinstance(output, Mapping) else {"result": output}
                )
                result = StepResult(
                    step=name,
                    status=FlowStatus.SUCCEEDED,
                    output=merged,
                    started_at=started,
                    finished_at=time.time(),
                )
                await self._fire(self.on_step_end, result)
                return result
            except BaseException as exc:
                last_error = exc
                attempt += 1
                if attempt > self.config.max_retries:
                    break
        result = StepResult(
            step=name,
            status=FlowStatus.FAILED,
            error=str(last_error),
            started_at=started,
            finished_at=time.time(),
        )
        await self._fire(self.on_step_end, result)
        return result

    @staticmethod
    async def _fire(
        hook: Callable[..., Awaitable[None] | None] | None, *args: Any
    ) -> None:
        if hook is None:
            return
        result = hook(*args)
        if inspect.isawaitable(result):
            await result

    # ------------------------------------------------------------------
    # 跨层适配
    # ------------------------------------------------------------------
    def as_tool(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> AgentTool:
        """将 Flow 包装为 LangGraph Agent 可调用的工具（Flow-as-Tool）。

        返回的 :class:`AgentTool` 接受任意输入字典，触发 :meth:`arun` 并返回
        最终上下文字典（包含所有 Step 累积输出）。
        """
        from ..agents.graph_agent import AgentTool

        tool_name = name or f"flow_{self.config.name}"
        tool_desc = (
            description or self.config.description or f"调用 Flow '{self.config.name}'"
        )

        async def _runner(query: Any = None, /, **kwargs: Any) -> dict[str, Any]:
            payload = (
                kwargs if kwargs else ({"input": query} if query is not None else {})
            )
            results = await self.arun(payload)
            return {
                "status": self._status.value,
                "run_id": self._run_id,
                "results": [r.model_dump() for r in results],
                "artifacts": [a.model_dump() for a in self._artifacts],
            }

        return AgentTool(name=tool_name, description=tool_desc, func=_runner)


# ---------------------------------------------------------------------------
# 预置 EvalFlow 模板
# ---------------------------------------------------------------------------


class EvalFlow(HarnessFlow):
    """评估 Flow 模板。

    标准骨架::

        start → prepare_data → run_agent → collect_metrics → report → end

    每步遵守明确的数据协议：

    * ``start``\\ ：初始化运行上下文，写入 ``run_id``\\ 、``started_at``\\ ；
    * ``prepare_data``\\ ：产出 ``dataset``\\ （评估样本列表）；
    * ``run_agent``\\ ：在 ``dataset`` 上运行被评 Agent，产出 ``predictions``\\ ；
    * ``collect_metrics``\\ ：汇总 ``predictions`` → ``metrics`` 字典；
    * ``report``\\ ：基于 ``metrics`` 产出最终 ``report``\\ ；
    * ``end``\\ ：标记完成并落盘汇总产物。

    子类通常重写 :meth:`prepare_data` / :meth:`run_agent` / :meth:`collect_metrics`
    三个方法即可定制完整评估链路。
    """

    def steps(self) -> list[tuple[str, StepFn]]:
        """声明评估骨架的 Step 序列。"""
        return [
            ("start", self.start),
            ("prepare_data", self.prepare_data),
            ("run_agent", self.run_agent),
            ("collect_metrics", self.collect_metrics),
            ("report", self.report),
            ("end", self.end),
        ]

    # ------------------------------------------------------------------
    # 可重写钩子
    # ------------------------------------------------------------------
    async def start(self, context: dict[str, Any]) -> dict[str, Any]:
        """初始化评估上下文。"""
        return {"started_at": time.time(), "run_id": self._run_id}

    async def prepare_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """准备评估数据集。子类应在此返回 ``{"dataset": [...]}``。"""
        dataset = list(context.get("dataset") or [])
        self.emit_artifact("dataset", dataset, step="prepare_data", size=len(dataset))
        return {"dataset": dataset}

    async def run_agent(self, context: dict[str, Any]) -> dict[str, Any]:
        """在数据集上运行被评 Agent。子类应在此返回 ``{"predictions": [...]}``。"""
        dataset = context.get("dataset") or []
        predictions = list(context.get("predictions") or [{} for _ in dataset])
        self.emit_artifact(
            "predictions", predictions, step="run_agent", size=len(predictions)
        )
        return {"predictions": predictions}

    async def collect_metrics(self, context: dict[str, Any]) -> dict[str, Any]:
        """汇总评估指标。子类应在此返回 ``{"metrics": {...}}``。"""
        predictions = context.get("predictions") or []
        metrics: dict[str, Any] = {"sample_count": len(predictions)}
        self.emit_artifact("metrics", metrics, step="collect_metrics")
        return {"metrics": metrics}

    async def report(self, context: dict[str, Any]) -> dict[str, Any]:
        """生成最终评估报告。子类可在此渲染表格 / 写入文件等。"""
        report_payload = {
            "run_id": self._run_id,
            "metrics": context.get("metrics") or {},
            "generated_at": time.time(),
        }
        self.emit_artifact("report", report_payload, step="report")
        return {"report": report_payload}

    async def end(self, context: dict[str, Any]) -> dict[str, Any]:
        """落盘汇总产物并标记完成。"""
        return {
            "completed_at": time.time(),
            "artifact_count": len(self._artifacts),
        }
