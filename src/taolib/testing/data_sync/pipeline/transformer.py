"""数据转换器。

实现字段映射和自定义 Python 函数转换。
"""

import importlib
import logging
from collections.abc import Callable
from typing import Any

from taolib.testing.data_sync.pipeline.protocols import TransformContext, TransformResult
from taolib.testing.data_sync.pipeline.utils import truncate_snapshot

logger = logging.getLogger(__name__)


class TransformChain:
    """数据转换链。

    按顺序应用：
    1. 字段映射
    2. 自定义转换函数（如果有）
    3. 验证
    """

    def __init__(
        self,
        field_mapping: dict[str, str] | None = None,
        transform_module_path: str | None = None,
    ) -> None:
        """初始化转换链。

        Args:
            field_mapping: 字段映射字典 {old_field: new_field}
            transform_module_path: 转换函数模块路径（如 "myapp.transforms.clean"）
        """
        self._field_mapping = field_mapping or {}
        self._transform_fn: Callable | None = None

        if transform_module_path:
            self._transform_fn = self._load_transform_fn(transform_module_path)

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
            转换结果
        """
        success: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []

        for doc in documents:
            try:
                transformed = self._apply_field_mapping(doc)

                if self._transform_fn:
                    result = self._transform_fn(transformed)
                    if result is None:
                        # 转换函数返回 None 表示跳过
                        continue
                    transformed = result

                success.append(transformed)

            except Exception as e:
                failures.append(
                    {
                        "document_id": doc.get("_id", "unknown"),
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "document_snapshot": truncate_snapshot(doc),
                    }
                )

        return TransformResult(transformed=success, failures=failures)

    def _apply_field_mapping(self, doc: dict[str, Any]) -> dict[str, Any]:
        """应用字段映射。"""
        if not self._field_mapping:
            return doc

        result = {}
        for key, value in doc.items():
            new_key = self._field_mapping.get(key, key)
            result[new_key] = value
        return result

    def _load_transform_fn(self, module_path: str) -> Callable | None:
        """动态加载转换函数。"""
        try:
            module = importlib.import_module(module_path)
            return getattr(module, "transform", None)
        except ImportError:
            return None


