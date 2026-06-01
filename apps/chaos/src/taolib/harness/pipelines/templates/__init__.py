"""Pipeline 模板集合 - 预置可复用的 Flow 结构模板与工厂方法。

通过 :class:`FlowTemplate` 枚举对外暴露内置模板的标识，并提供
:func:`create_from_template` 作为统一的工厂入口。

示例::

    from taolib.harness.pipelines.templates import FlowTemplate, create_from_template

    flow = create_from_template(
        FlowTemplate.EVAL,
        config={"name": "rag-eval", "version": "0.1.0"},
    )
    results = flow.run({"dataset": [...]})

新模板可通过 :func:`register_template` 注入到全局表中。
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from enum import StrEnum
from typing import Any

from ..flow_base import EvalFlow, FlowConfig, HarnessFlow, StepFn

__all__ = [
    "ETLFlow",
    "FlowTemplate",
    "TrainingFlow",
    "create_from_template",
    "register_template",
]


class FlowTemplate(StrEnum):
    """预置 Flow 模板枚举。"""

    EVAL = "eval"
    ETL = "etl"
    TRAINING = "training"


class ETLFlow(HarnessFlow):
    """ETL 数据处理 Flow 模板。

    标准骨架：``extract → transform → load → end``，子类按需重写各 Step。
    """

    def steps(self) -> list[tuple[str, StepFn]]:
        return [
            ("extract", self.extract),
            ("transform", self.transform),
            ("load", self.load),
            ("end", self.end),
        ]

    async def extract(self, context: dict[str, Any]) -> dict[str, Any]:
        """抽取原始数据。子类应返回 ``{"raw": [...]}``。"""
        return {"raw": context.get("raw") or []}

    async def transform(self, context: dict[str, Any]) -> dict[str, Any]:
        """转换数据。子类应返回 ``{"transformed": [...]}``。"""
        raw = context.get("raw") or []
        return {"transformed": list(raw)}

    async def load(self, context: dict[str, Any]) -> dict[str, Any]:
        """落盘 / 写库。子类应返回 ``{"loaded": int}``。"""
        transformed = context.get("transformed") or []
        self.emit_artifact("loaded", transformed, step="load", size=len(transformed))
        return {"loaded": len(transformed)}

    async def end(self, context: dict[str, Any]) -> dict[str, Any]:
        return {"completed_at": time.time()}


class TrainingFlow(HarnessFlow):
    """模型训练 Flow 模板。

    标准骨架：``prepare → train → evaluate → checkpoint → end``。
    """

    def steps(self) -> list[tuple[str, StepFn]]:
        return [
            ("prepare", self.prepare),
            ("train", self.train),
            ("evaluate", self.evaluate),
            ("checkpoint", self.checkpoint),
            ("end", self.end),
        ]

    async def prepare(self, context: dict[str, Any]) -> dict[str, Any]:
        """准备训练数据与超参。"""
        return {"hparams": context.get("hparams") or {}}

    async def train(self, context: dict[str, Any]) -> dict[str, Any]:
        """执行训练循环。子类应返回 ``{"model": ...}``。"""
        return {"model": context.get("model")}

    async def evaluate(self, context: dict[str, Any]) -> dict[str, Any]:
        """在验证集上评估。"""
        return {"eval_metrics": {}}

    async def checkpoint(self, context: dict[str, Any]) -> dict[str, Any]:
        """保存模型检查点。"""
        self.emit_artifact("checkpoint", context.get("model"), step="checkpoint")
        return {"checkpoint_saved": True}

    async def end(self, context: dict[str, Any]) -> dict[str, Any]:
        return {"completed_at": time.time()}


# ---------------------------------------------------------------------------
# 模板注册表
# ---------------------------------------------------------------------------
_TEMPLATES: dict[FlowTemplate, type[HarnessFlow]] = {
    FlowTemplate.EVAL: EvalFlow,
    FlowTemplate.ETL: ETLFlow,
    FlowTemplate.TRAINING: TrainingFlow,
}


def register_template(
    template: FlowTemplate | str, flow_cls: type[HarnessFlow]
) -> None:
    """注册一个新的 Flow 模板（或覆盖已有模板）。"""
    key = FlowTemplate(template) if isinstance(template, str) else template
    _TEMPLATES[key] = flow_cls


def create_from_template(
    template: FlowTemplate | str,
    config: FlowConfig | Mapping[str, Any],
    /,
    **kwargs: Any,
) -> HarnessFlow:
    """根据模板枚举构造 Flow 实例。

    Args:
        template: 模板枚举或其字符串值。
        config: Flow 配置（``FlowConfig`` 或可被其校验的字典）。
        **kwargs: 透传给具体 Flow 构造函数的额外参数（如 ``registry``、
            ``auto_register`` 等）。

    Raises:
        KeyError: 当模板未注册时抛出。
    """
    key = FlowTemplate(template) if isinstance(template, str) else template
    try:
        cls = _TEMPLATES[key]
    except KeyError as exc:  # pragma: no cover - 枚举范围有限
        raise KeyError(f"未注册的 Flow 模板: {template!r}") from exc
    return cls(config, **kwargs)


type _TemplateFactory = Callable[[FlowConfig | Mapping[str, Any]], HarnessFlow]
