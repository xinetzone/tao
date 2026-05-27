"""轻量级客户端 SDK。

提供同步和异步的文件存储访问接口。
"""

import hashlib
import mimetypes
from pathlib import Path
from typing import Any

import httpx


class FileStorageClient:
    """文件存储客户端。"""

    def __init__(
        self,
        base_url: str = "http://localhost:8002",
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._headers: dict[str, str] = {}
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self._base_url,
            headers=self._headers,
            timeout=self._timeout,
        )

    def _async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=self._timeout,
        )

    # === Bucket 操作 ===

    def create_bucket(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """创建存储桶。"""
        data = {"name": name, **kwargs}
        with self._client() as client:
            response = client.post("/api/v1/buckets", json=data)
            response.raise_for_status()
            return response.json()

    def list_buckets(self) -> list[dict[str, Any]]:
        """列出所有存储桶。"""
        with self._client() as client:
            response = client.get("/api/v1/buckets")
            response.raise_for_status()
            return response.json()

    # === 文件操作 ===

    def upload_file(
        self,
        bucket_id: str,
        file_path: str | Path,
        object_key: str,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        """上传文件。

        自动根据文件大小选择简单上传或分片上传。
        """
        path = Path(file_path)
        if not content_type:
            content_type, _ = mimetypes.guess_type(str(path))
            content_type = content_type or "application/octet-stream"

        with self._client() as client, open(path, "rb") as f:
            files = {"file": (path.name, f, content_type)}
            response = client.post(
                "/api/v1/files/upload",
                files=files,
                params={
                    "bucket_id": bucket_id,
                    "object_key": object_key,
                },
            )
            response.raise_for_status()
            return response.json()

    def download_file(self, file_id: str, dest_path: str | Path) -> Path:
        """下载文件。"""
        dest = Path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with (
            self._client() as client,
            client.stream("GET", f"/api/v1/files/{file_id}/download") as response,
        ):
            response.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
        return dest

    def get_file(self, file_id: str) -> dict[str, Any]:
        """获取文件元数据。"""
        with self._client() as client:
            response = client.get(f"/api/v1/files/{file_id}")
            response.raise_for_status()
            return response.json()

    def delete_file(self, file_id: str) -> bool:
        """删除文件。"""
        with self._client() as client:
            response = client.delete(f"/api/v1/files/{file_id}")
            response.raise_for_status()
            return response.status_code == 204

    def list_files(
        self,
        bucket_id: str | None = None,
        prefix: str | None = None,
    ) -> list[dict[str, Any]]:
        """列出文件。"""
        params: dict[str, str] = {}
        if bucket_id:
            params["bucket_id"] = bucket_id
        if prefix:
            params["prefix"] = prefix
        with self._client() as client:
            response = client.get("/api/v1/files", params=params)
            response.raise_for_status()
            return response.json()

    def get_file_url(self, file_id: str, expires_in: int = 3600) -> str:
        """获取文件访问 URL。"""
        with self._client() as client:
            response = client.get(
                f"/api/v1/files/{file_id}/url",
                params={"expires_in": expires_in},
            )
            response.raise_for_status()
            return response.json()["url"]

    # === 分片上传 ===

    def init_upload(
        self,
        bucket_id: str,
        object_key: str,
        filename: str,
        content_type: str,
        total_size_bytes: int,
        chunk_size_bytes: int = 5 * 1024 * 1024,
    ) -> dict[str, Any]:
        """初始化分片上传。"""
        total_chunks = (total_size_bytes + chunk_size_bytes - 1) // chunk_size_bytes
        data = {
            "bucket_id": bucket_id,
            "object_key": object_key,
            "original_filename": filename,
            "content_type": content_type,
            "total_size_bytes": total_size_bytes,
            "chunk_size_bytes": chunk_size_bytes,
            "total_chunks": total_chunks,
        }
        with self._client() as client:
            response = client.post("/api/v1/uploads", json=data)
            response.raise_for_status()
            return response.json()

    def upload_chunk(
        self,
        session_id: str,
        chunk_index: int,
        data: bytes,
        checksum: str | None = None,
    ) -> dict[str, Any]:
        """上传分片。"""
        if not checksum:
            checksum = hashlib.sha256(data).hexdigest()
        with self._client() as client:
            files = {"file": ("chunk", data, "application/octet-stream")}
            response = client.put(
                f"/api/v1/uploads/{session_id}/chunks/{chunk_index}",
                files=files,
                params={"checksum": checksum},
            )
            response.raise_for_status()
            return response.json()

    def complete_upload(self, session_id: str) -> dict[str, Any]:
        """完成分片上传。"""
        with self._client() as client:
            response = client.post(f"/api/v1/uploads/{session_id}/complete")
            response.raise_for_status()
            return response.json()

    def abort_upload(self, session_id: str) -> bool:
        """中止分片上传。"""
        with self._client() as client:
            response = client.post(f"/api/v1/uploads/{session_id}/abort")
            response.raise_for_status()
            return response.json().get("success", False)

    def get_upload_status(self, session_id: str) -> dict[str, Any]:
        """获取上传状态。"""
        with self._client() as client:
            response = client.get(f"/api/v1/uploads/{session_id}")
            response.raise_for_status()
            return response.json()
