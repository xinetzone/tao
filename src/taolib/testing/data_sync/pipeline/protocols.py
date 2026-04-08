"""Pipeline Protocol 定义。

定义 Extractor, Transformer, Loader 的接口契约。
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

from motor.motor_asyncio import AsyncIOMotorCollection

from taolib.testing.data_sync.models.checkpoint import SyncCheckpoint


@dataclass
class TransformContext:
    """转换上下文。"""

    job_id: str
    collection_name: str
    field_mapping: dict[str, str] | None = None
    transform_fn: Any | None = None


@dataclass
class TransformResult:
    """转换结果。"""

    transformed: list[dict[str, Any]]
    failures: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class LoadResult:
    """加载结果。"""

    inserted: int
    updated: int
    failed: int
    failures: list[dict[str, Any]] = field(default_factory=list)


class ExtractorProtocol(Protocol):
    """数据提取器 Protocol。"""

    async def extract(
        self,
        source_collection: AsyncIOMotorCollection,
        checkpoint: SyncCheckpoint | None,
        filter_query: dict[str, Any] | None,
        batch_size: int,
    ) -> Any:
        """分批提取源数据。

        Args:
            source_collection: 源集合
            checkpoint: 检查点（增量同步时使用）
            filter_query: 过滤查询
            batch_size: 批次大小

        Yields:
            文档批次列表
        """
        ...


class TransformerProtocol(Protocol):
    """数据转换器 Protocol。"""

    async def transform(
        self,
        documents: list[dict[str, Any]],
        context: TransformContext,
    ) -> TransformResult:
        """转换文档批次。

        Args:
            documents: 文档列表
            context: 转换上下文

        Returns:
            转换结果（成功文档 + 失败记录）
        """
        ...


class LoaderProtocol(Protocol):
    """数据加载器 Protocol。"""

    async def load(
        self,
        target_collection: AsyncIOMotorCollection,
        documents: list[dict[str, Any]],
    ) -> LoadResult:
        """加载文档到目标集合。

        Args:
            target_collection: 目标集合
            documents: 文档列表

        Returns:
            加载结果
        """
        ...


@dataclass
class ValidateResult:
    """验证结果。"""

    valid: list[dict[str, Any]]
    failures: list[dict[str, Any]] = field(default_factory=list)


class ValidatorProtocol(Protocol):
    """数据验证器 Protocol。"""

    async def validate(
        self,
        documents: list[dict[str, Any]],
        context: TransformContext,
    ) -> ValidateResult:
        """验证文档批次。

        Args:
            documents: 文档列表
            context: 转换上下文

        Returns:
            验证结果（通过的文档 + 失败记录）
        """
        ...


