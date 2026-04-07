"""测试存储后端。"""

import tempfile

import pytest

from taolib.file_storage.errors import StorageBackendError
from taolib.file_storage.storage.local_backend import LocalStorageBackend


class TestLocalStorageBackend:
    """测试本地文件系统存储后端。"""

    @pytest.fixture
    def tmp_dir(self):
        """提供临时目录。"""
        with tempfile.TemporaryDirectory() as d:
            yield d

    @pytest.fixture
    def backend(self, tmp_dir: str) -> LocalStorageBackend:
        return LocalStorageBackend(tmp_dir)

    @pytest.mark.asyncio
    async def test_create_bucket(self, backend: LocalStorageBackend) -> None:
        await backend.create_bucket("test-bucket")
        assert await backend.bucket_exists("test-bucket")

    @pytest.mark.asyncio
    async def test_bucket_exists_false(self, backend: LocalStorageBackend) -> None:
        assert not await backend.bucket_exists("nonexistent")

    @pytest.mark.asyncio
    async def test_put_and_get_object(self, backend: LocalStorageBackend) -> None:
        data = b"Hello, world!"
        await backend.create_bucket("test-bucket")
        await backend.put_object("test-bucket", "hello.txt", data)

        stream = await backend.get_object("test-bucket", "hello.txt")
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        assert b"".join(chunks) == data

    @pytest.mark.asyncio
    async def test_delete_object(self, backend: LocalStorageBackend) -> None:
        await backend.create_bucket("test-bucket")
        await backend.put_object("test-bucket", "file.txt", b"content")

        deleted = await backend.delete_object("test-bucket", "file.txt")
        assert deleted is True

        exists = await backend.object_exists("test-bucket", "file.txt")
        assert exists is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_object(
        self, backend: LocalStorageBackend
    ) -> None:
        deleted = await backend.delete_object("test-bucket", "nope.txt")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_copy_object(self, backend: LocalStorageBackend) -> None:
        await backend.create_bucket("src-bucket")
        await backend.create_bucket("dst-bucket")
        await backend.put_object("src-bucket", "src.txt", b"content")

        result = await backend.copy_object(
            "src-bucket", "src.txt", "dst-bucket", "dst.txt"
        )
        assert result.storage_path == "dst-bucket/dst.txt"

        exists = await backend.object_exists("dst-bucket", "dst.txt")
        assert exists is True

    @pytest.mark.asyncio
    async def test_head_object(self, backend: LocalStorageBackend) -> None:
        data = b"some data"
        await backend.create_bucket("test-bucket")
        await backend.put_object("test-bucket", "test.txt", data)

        info = await backend.head_object("test-bucket", "test.txt")
        assert info.size == len(data)
        assert info.key == "test.txt"

    @pytest.mark.asyncio
    async def test_head_object_not_found(self, backend: LocalStorageBackend) -> None:
        with pytest.raises(StorageBackendError):
            await backend.head_object("test-bucket", "nope.txt")

    @pytest.mark.asyncio
    async def test_multipart_upload(self, backend: LocalStorageBackend) -> None:
        await backend.create_bucket("test-bucket")

        upload_id = await backend.create_multipart_upload(
            "test-bucket", "video.mp4", "video/mp4"
        )
        assert upload_id is not None

        part1 = await backend.upload_part(
            "test-bucket", "video.mp4", upload_id, 1, b"part1"
        )
        assert part1.part_number == 1

        part2 = await backend.upload_part(
            "test-bucket", "video.mp4", upload_id, 2, b"part2"
        )

        result = await backend.complete_multipart_upload(
            "test-bucket",
            "video.mp4",
            upload_id,
            [part1, part2],
        )
        assert result.storage_path == "test-bucket/video.mp4"

    @pytest.mark.asyncio
    async def test_abort_multipart_upload(self, backend: LocalStorageBackend) -> None:
        await backend.create_bucket("test-bucket")

        upload_id = await backend.create_multipart_upload("test-bucket", "file.bin")
        await backend.abort_multipart_upload("test-bucket", "file.bin", upload_id)

    @pytest.mark.asyncio
    async def test_delete_bucket(self, backend: LocalStorageBackend) -> None:
        await backend.create_bucket("temp-bucket")
        assert await backend.bucket_exists("temp-bucket")

        await backend.delete_bucket("temp-bucket")
        assert not await backend.bucket_exists("temp-bucket")

    @pytest.mark.asyncio
    async def test_list_objects(self, backend: LocalStorageBackend) -> None:
        await backend.create_bucket("test-bucket")
        await backend.put_object("test-bucket", "a.txt", b"a")
        await backend.put_object("test-bucket", "b.txt", b"b")

        objects, _ = await backend.list_objects("test-bucket")
        assert len(objects) == 2

    @pytest.mark.asyncio
    async def test_generate_presigned_url(self, backend: LocalStorageBackend) -> None:
        url = await backend.generate_presigned_url(
            "test-bucket", "file.txt", expires_in=3600
        )
        assert "test-bucket" in url
        assert "file.txt" in url
