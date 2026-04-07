"""数据验证器。

在 Transform 和 Load 之间对文档进行验证。
"""

import logging
from collections.abc import Callable
from typing import Any

from taolib.data_sync.pipeline.protocols import TransformContext, ValidateResult
from taolib.data_sync.pipeline.utils import truncate_snapshot

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器。

    支持注册多个验证函数，在文档写入目标数据库前进行校验。

    每个验证函数签名为::

        def my_validator(doc: dict, ctx: TransformContext) -> list[str]

    返回空列表表示验证通过，否则返回错误消息列表。
    """

    def __init__(self) -> None:
        """初始化验证器。"""
        self._validators: list[
            Callable[[dict[str, Any], TransformContext], list[str]]
        ] = []

    def register(
        self,
        fn: Callable[[dict[str, Any], TransformContext], list[str]],
    ) -> None:
        """注册验证函数。

        Args:
            fn: 验证函数，接收文档和上下文，返回错误消息列表
        """
        self._validators.append(fn)

    async def validate(
        self,
        documents: list[dict[str, Any]],
        context: TransformContext,
    ) -> ValidateResult:
        """验证文档批次。

        Args:
            documents: 待验证的文档列表
            context: 转换上下文

        Returns:
            验证结果（通过的文档 + 失败记录）
        """
        if not self._validators:
            return ValidateResult(valid=documents, failures=[])

        valid: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []

        for doc in documents:
            errors: list[str] = []
            for validator_fn in self._validators:
                try:
                    result = validator_fn(doc, context)
                    errors.extend(result)
                except Exception as e:
                    errors.append(f"{type(e).__name__}: {e}")

            if errors:
                failures.append(
                    {
                        "document_id": doc.get("_id", "unknown"),
                        "error_type": "ValidationError",
                        "error_message": "; ".join(errors),
                        "document_snapshot": truncate_snapshot(doc),
                    }
                )
                logger.debug(
                    "文档 %s 验证失败: %s",
                    doc.get("_id", "unknown"),
                    errors,
                )
            else:
                valid.append(doc)

        return ValidateResult(valid=valid, failures=failures)
