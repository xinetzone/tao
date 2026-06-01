"""注册表 - 管理 Agent 图和 Metaflow Flow 的注册、发现和生命周期。

本模块提供三个层次的注册能力：

* :class:`AgentRegistry` —— LangGraph Agent / 子图定义的注册中心；
* :class:`FlowRegistry` —— Metaflow Flow 模板的注册中心；
* :class:`UnifiedRegistry` —— 组合两者并提供统一的发现接口。

注册条目通过 :class:`RegistryEntry` 描述元数据（版本、标签、描述等），
支持装饰器风格的便捷注册：``@register_agent(name=..., version=...)``。
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "AgentRegistry",
    "FlowRegistry",
    "RegistryEntry",
    "UnifiedRegistry",
    "register_agent",
    "register_flow",
]


T = TypeVar("T")


class RegistryEntry(BaseModel, Generic[T]):
    """注册表条目元数据。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: str
    version: str = Field(default="0.1.0", description="语义化版本号")
    tags: tuple[str, ...] = Field(default_factory=tuple)
    description: str = ""
    component: Any = Field(
        default=None, description="实际注册对象，如图工厂或 FlowSpec 类"
    )


class _BaseRegistry(Generic[T]):
    """注册表基类 - 提供按 ``(name, version)`` 唯一索引的存储。"""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], RegistryEntry[T]] = {}

    # ------------------------------------------------------------------
    # 注册 / 注销
    # ------------------------------------------------------------------
    def register(
        self,
        component: T,
        *,
        name: str,
        version: str = "0.1.0",
        tags: Iterable[str] = (),
        description: str = "",
        overwrite: bool = False,
    ) -> RegistryEntry[T]:
        """注册一个组件。

        Args:
            component: 待注册的对象。
            name: 唯一名称。
            version: 语义化版本号。
            tags: 用于过滤的标签集合。
            description: 描述信息。
            overwrite: 同名同版本存在时是否覆盖。
        """
        key = (name, version)
        if key in self._entries and not overwrite:
            raise ValueError(
                f"组件已存在: {name}@{version}; 设置 overwrite=True 以覆盖"
            )
        entry = RegistryEntry[T](
            name=name,
            version=version,
            tags=tuple(tags),
            description=description,
            component=component,
        )
        self._entries[key] = entry
        return entry

    def unregister(self, name: str, version: str | None = None) -> int:
        """注销指定名称的组件，返回被移除的条目数。"""
        if version is not None:
            return 1 if self._entries.pop((name, version), None) is not None else 0
        keys = [k for k in self._entries if k[0] == name]
        for k in keys:
            del self._entries[k]
        return len(keys)

    # ------------------------------------------------------------------
    # 查询 / 发现
    # ------------------------------------------------------------------
    def get(self, name: str, version: str | None = None) -> RegistryEntry[T]:
        """获取指定组件；缺省返回该名称下最新版本（按字符串排序）。"""
        if version is not None:
            try:
                return self._entries[(name, version)]
            except KeyError as exc:
                raise KeyError(f"未找到组件: {name}@{version}") from exc
        candidates = [e for (n, _), e in self._entries.items() if n == name]
        if not candidates:
            raise KeyError(f"未找到组件: {name}")
        candidates.sort(key=lambda e: e.version, reverse=True)
        return candidates[0]

    def has(self, name: str, version: str | None = None) -> bool:
        """判断组件是否已注册。"""
        try:
            self.get(name, version)
        except KeyError:
            return False
        return True

    def list(
        self,
        *,
        tags: Iterable[str] | None = None,
        name_prefix: str | None = None,
    ) -> list[RegistryEntry[T]]:
        """列出符合条件的全部条目。"""
        tag_set = set(tags or ())
        results: list[RegistryEntry[T]] = []
        for entry in self._entries.values():
            if name_prefix and not entry.name.startswith(name_prefix):
                continue
            if tag_set and not tag_set.issubset(entry.tags):
                continue
            results.append(entry)
        results.sort(key=lambda e: (e.name, e.version))
        return results

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, item: str | tuple[str, str]) -> bool:
        if isinstance(item, tuple):
            return item in self._entries
        return any(n == item for n, _ in self._entries)


class AgentRegistry(_BaseRegistry[Any]):
    """LangGraph Agent / 子图定义注册表。"""

    def get_component(self, name: str, version: str | None = None) -> Any:
        """直接返回注册条目中的 ``component`` 对象。"""
        return self.get(name, version).component


class FlowRegistry(_BaseRegistry[Any]):
    """Metaflow Flow 模板注册表。"""

    def get_component(self, name: str, version: str | None = None) -> Any:
        """直接返回注册条目中的 ``component`` 对象。"""
        return self.get(name, version).component


class UnifiedRegistry:
    """统一注册表 - 组合 :class:`AgentRegistry` 与 :class:`FlowRegistry`。

    通过 :meth:`discover` 可在两侧同时检索；通过 :meth:`agents`/:meth:`flows`
    访问各自的子注册表。
    """

    def __init__(
        self,
        *,
        agents: AgentRegistry | None = None,
        flows: FlowRegistry | None = None,
    ) -> None:
        self._agents = agents or AgentRegistry()
        self._flows = flows or FlowRegistry()

    @property
    def agents(self) -> AgentRegistry:
        """Agent 子注册表。"""
        return self._agents

    @property
    def flows(self) -> FlowRegistry:
        """Flow 子注册表。"""
        return self._flows

    def discover(
        self,
        *,
        tags: Iterable[str] | None = None,
        name_prefix: str | None = None,
    ) -> dict[str, list[RegistryEntry[Any]]]:
        """跨注册表发现组件，返回按类型分组的结果。"""
        return {
            "agents": self._agents.list(tags=tags, name_prefix=name_prefix),
            "flows": self._flows.list(tags=tags, name_prefix=name_prefix),
        }

    def stats(self) -> dict[str, int]:
        """返回各子注册表的条目数量。"""
        return {"agents": len(self._agents), "flows": len(self._flows)}


# ----------------------------------------------------------------------
# 装饰器
# ----------------------------------------------------------------------
_DEFAULT_REGISTRY = UnifiedRegistry()


def get_default_registry() -> UnifiedRegistry:
    """获取模块级默认 :class:`UnifiedRegistry` 实例。"""
    return _DEFAULT_REGISTRY


def register_agent(
    *,
    name: str,
    version: str = "0.1.0",
    tags: Iterable[str] = (),
    description: str = "",
    registry: UnifiedRegistry | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    """装饰器：将被装饰对象注册为 LangGraph Agent。

    Example::

        @register_agent(name="planner", version="1.0.0", tags=("plan",))
        def build_planner_graph(): ...
    """

    def decorator(component: T) -> T:
        target = (registry or _DEFAULT_REGISTRY).agents
        target.register(
            component,
            name=name,
            version=version,
            tags=tags,
            description=description,
            overwrite=overwrite,
        )
        return component

    return decorator


def register_flow(
    *,
    name: str,
    version: str = "0.1.0",
    tags: Iterable[str] = (),
    description: str = "",
    registry: UnifiedRegistry | None = None,
    overwrite: bool = False,
) -> Callable[[T], T]:
    """装饰器：将被装饰对象注册为 Metaflow Flow。"""

    def decorator(component: T) -> T:
        target = (registry or _DEFAULT_REGISTRY).flows
        target.register(
            component,
            name=name,
            version=version,
            tags=tags,
            description=description,
            overwrite=overwrite,
        )
        return component

    return decorator


__all__ = [*__all__, "get_default_registry"]
