"""truncate_snapshot 工具函数测试。"""

from taolib.data_sync.pipeline.utils import truncate_snapshot


class TestTruncateSnapshot:
    """文档快照截断测试。"""

    def test_empty_doc(self) -> None:
        """空字典原样返回。"""
        assert truncate_snapshot({}) == {}

    def test_small_doc_unchanged(self) -> None:
        """小文档不截断。"""
        doc = {"_id": "1", "name": "test", "value": 42}
        result = truncate_snapshot(doc)
        assert result == doc
        assert "__truncated__" not in result

    def test_preserves_id(self) -> None:
        """截断后保留 _id 字段。"""
        # 构造一个超大文档
        doc = {"_id": "doc-123"}
        for i in range(200):
            doc[f"field_{i}"] = "x" * 100
        result = truncate_snapshot(doc, max_bytes=1024)
        assert result["_id"] == "doc-123"
        assert result["__truncated__"] is True

    def test_large_doc_truncated(self) -> None:
        """大文档被截断。"""
        doc = {"_id": "1", "data": "x" * 10000}
        result = truncate_snapshot(doc, max_bytes=4096)
        assert "__truncated__" in result
        assert result["_id"] == "1"

    def test_custom_max_bytes(self) -> None:
        """自定义最大字节数。"""
        doc = {"_id": "1", "a": "hello", "b": "x" * 500}
        result = truncate_snapshot(doc, max_bytes=100)
        assert result["__truncated__"] is True
        assert result["_id"] == "1"

    def test_non_serializable_value(self) -> None:
        """包含不可序列化值时不崩溃。"""
        doc = {"_id": "1", "obj": object()}
        result = truncate_snapshot(doc)
        # default=str 会处理，不应抛异常
        assert "_id" in result

    def test_within_limit_no_truncation(self) -> None:
        """刚好在限制内不截断。"""
        doc = {"_id": "1", "val": "a"}
        result = truncate_snapshot(doc, max_bytes=4096)
        assert result == doc
        assert "__truncated__" not in result
