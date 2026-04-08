"""DataValidator 测试。"""

import pytest

from taolib.testing.data_sync.pipeline.protocols import TransformContext, ValidateResult
from taolib.testing.data_sync.pipeline.validator import DataValidator


class TestDataValidator:
    """数据验证器测试。"""

    @pytest.fixture
    def context(self) -> TransformContext:
        return TransformContext(job_id="job1", collection_name="users")

    @pytest.mark.asyncio
    async def test_no_rules_passes_all(self, context) -> None:
        """没有注册规则时全部通过。"""
        validator = DataValidator()
        docs = [{"_id": "1", "name": "Alice"}, {"_id": "2", "name": "Bob"}]
        result = await validator.validate(docs, context)
        assert len(result.valid) == 2
        assert len(result.failures) == 0

    @pytest.mark.asyncio
    async def test_rejects_invalid(self, context) -> None:
        """验证函数拒绝无效文档。"""
        validator = DataValidator()

        def require_name(doc, ctx):
            if "name" not in doc:
                return ["缺少 name 字段"]
            return []

        validator.register(require_name)

        docs = [
            {"_id": "1", "name": "Alice"},
            {"_id": "2"},  # 缺少 name
        ]
        result = await validator.validate(docs, context)
        assert len(result.valid) == 1
        assert len(result.failures) == 1
        assert result.valid[0]["_id"] == "1"
        assert result.failures[0]["document_id"] == "2"
        assert "name" in result.failures[0]["error_message"]

    @pytest.mark.asyncio
    async def test_multiple_rules(self, context) -> None:
        """多个规则同时生效。"""
        validator = DataValidator()

        def require_name(doc, ctx):
            return ["缺少 name"] if "name" not in doc else []

        def require_email(doc, ctx):
            return ["缺少 email"] if "email" not in doc else []

        validator.register(require_name)
        validator.register(require_email)

        docs = [
            {"_id": "1", "name": "Alice", "email": "a@b.com"},
            {"_id": "2", "name": "Bob"},  # 缺少 email
            {"_id": "3"},  # 缺少两者
        ]
        result = await validator.validate(docs, context)
        assert len(result.valid) == 1
        assert len(result.failures) == 2

        # 第三个文档应有两个错误消息
        failure_3 = next(f for f in result.failures if f["document_id"] == "3")
        assert "name" in failure_3["error_message"]
        assert "email" in failure_3["error_message"]

    @pytest.mark.asyncio
    async def test_validator_exception_handled(self, context) -> None:
        """验证函数抛异常不影响整体流程。"""
        validator = DataValidator()

        def buggy_validator(doc, ctx):
            raise RuntimeError("bug in validator")

        validator.register(buggy_validator)

        docs = [{"_id": "1", "name": "Alice"}]
        result = await validator.validate(docs, context)
        assert len(result.valid) == 0
        assert len(result.failures) == 1
        assert "RuntimeError" in result.failures[0]["error_message"]

    @pytest.mark.asyncio
    async def test_validate_result_type(self, context) -> None:
        """返回类型是 ValidateResult。"""
        validator = DataValidator()
        result = await validator.validate([{"_id": "1"}], context)
        assert isinstance(result, ValidateResult)

    @pytest.mark.asyncio
    async def test_failure_contains_snapshot(self, context) -> None:
        """失败记录包含文档快照。"""
        validator = DataValidator()
        validator.register(lambda doc, ctx: ["invalid"])

        docs = [{"_id": "1", "data": "test_value"}]
        result = await validator.validate(docs, context)
        assert len(result.failures) == 1
        snapshot = result.failures[0].get("document_snapshot")
        assert snapshot is not None
        assert snapshot["_id"] == "1"



