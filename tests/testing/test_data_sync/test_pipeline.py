"""Pipeline 组件测试。"""

import pytest

from taolib.testing.data_sync.pipeline.extractor import MongoExtractor
from taolib.testing.data_sync.pipeline.loader import MongoLoader
from taolib.testing.data_sync.pipeline.protocols import TransformContext
from taolib.testing.data_sync.pipeline.transformer import TransformChain


class TestMongoExtractor:
    """提取器测试。"""

    def test_extractor_init(self) -> None:
        extractor = MongoExtractor(batch_size=500)
        assert extractor._batch_size == 500

    def test_extractor_default_batch_size(self) -> None:
        extractor = MongoExtractor()
        assert extractor._batch_size == 1000


class TestTransformChain:
    """转换器测试。"""

    def test_field_mapping(self) -> None:
        chain = TransformChain(field_mapping={"old_name": "new_name"})
        doc = {"_id": "1", "old_name": "test"}
        result = chain._apply_field_mapping(doc)
        assert "new_name" in result
        assert "old_name" not in result
        assert result["new_name"] == "test"

    def test_no_field_mapping(self) -> None:
        chain = TransformChain()
        doc = {"_id": "1", "name": "test"}
        result = chain._apply_field_mapping(doc)
        assert result == doc

    @pytest.mark.asyncio
    async def test_transform_success(self) -> None:
        chain = TransformChain(field_mapping={"old": "new"})
        docs = [{"_id": "1", "old": "value1"}, {"_id": "2", "old": "value2"}]
        context = TransformContext(job_id="job1", collection_name="users")
        result = await chain.transform(docs, context)
        assert len(result.transformed) == 2
        assert len(result.failures) == 0
        assert result.transformed[0]["new"] == "value1"

    @pytest.mark.asyncio
    async def test_transform_with_failure(self) -> None:
        """测试转换失败处理"""

        def bad_transform(doc: dict) -> dict:
            if doc.get("_id") == "2":
                raise ValueError("Bad doc")
            return doc

        chain = TransformChain()
        chain._transform_fn = bad_transform
        docs = [{"_id": "1"}, {"_id": "2"}]
        context = TransformContext(job_id="job1", collection_name="users")
        result = await chain.transform(docs, context)
        assert len(result.transformed) == 1
        assert len(result.failures) == 1

    @pytest.mark.asyncio
    async def test_transform_failure_snapshot_truncated(self) -> None:
        """转换失败时文档快照应被截断。"""

        def always_fail(doc: dict) -> dict:
            raise ValueError("Fail")

        chain = TransformChain()
        chain._transform_fn = always_fail
        # 创建一个大文档
        big_doc = {"_id": "big", "data": "x" * 10000}
        context = TransformContext(job_id="job1", collection_name="users")
        result = await chain.transform([big_doc], context)
        assert len(result.failures) == 1
        snapshot = result.failures[0]["document_snapshot"]
        assert snapshot is not None
        assert snapshot["_id"] == "big"
        # 验证被截断了
        import json

        raw = json.dumps(snapshot, default=str, ensure_ascii=False)
        assert len(raw.encode("utf-8")) <= 4096


class TestMongoLoader:
    """加载器测试。"""

    def test_loader_exists(self) -> None:
        loader = MongoLoader()
        assert loader is not None



