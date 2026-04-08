"""S3 兼容存储后端。

支持 AWS S3、MinIO、阿里云 OSS 等所有 S3 兼容服务。
"""

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from taolib.testing.file_storage.errors import StorageBackendError
from taolib.testing.file_storage.storage.protocols import (
    ObjectInfo,
    PartInfo,
    PutObjectResult,
)


class S3StorageBackend:
    """S3 兼容存储后端实现。

    使用 aiobotocore 与 S3 兼容 API 交互。
    """

    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key: str = "",
        secret_key: str = "",
        region: str = "us-east-1",
    ) -> None:
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._session: Any = None

    def _get_session(self) -> Any:
        """延迟初始化 aiobotocore session。"""
        if self._session is None:
            from aiobotocore.session import AioSession

            self._session = AioSession()
        return self._session

    def _create_client(self) -> Any:
        """创建 S3 客户端上下文管理器。"""
        session = self._get_session()
        kwargs: dict[str, Any] = {
            "region_name": self._region,
            "aws_access_key_id": self._access_key,
            "aws_secret_access_key": self._secret_key,
        }
        if self._endpoint_url:
            kwargs["endpoint_url"] = self._endpoint_url
        return session.create_client("s3", **kwargs)

    async def put_object(
        self,
        bucket: str,
        key: str,
        data: bytes | AsyncIterator[bytes],
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> PutObjectResult:
        """上传对象到 S3。"""
        if isinstance(data, bytes):
            body = data
        else:
            chunks = []
            async for chunk in data:
                chunks.append(chunk)
            body = b"".join(chunks)

        kwargs: dict[str, Any] = {
            "Bucket": bucket,
            "Key": key,
            "Body": body,
            "ContentType": content_type,
        }
        if metadata:
            kwargs["Metadata"] = metadata

        try:
            async with self._create_client() as client:
                response = await client.put_object(**kwargs)
                return PutObjectResult(
                    storage_path=f"{bucket}/{key}",
                    etag=response.get("ETag", "").strip('"'),
                    version_id=response.get("VersionId"),
                )
        except Exception as e:
            raise StorageBackendError(f"S3 上传失败: {e}") from e

    async def get_object(self, bucket: str, key: str) -> AsyncIterator[bytes]:
        """从 S3 下载对象（流式）。"""
        try:
            async with self._create_client() as client:
                response = await client.get_object(Bucket=bucket, Key=key)
                stream = response["Body"]

                async def _stream() -> AsyncIterator[bytes]:
                    async with stream:
                        async for chunk in stream.iter_chunks():
                            yield chunk

                return _stream()
        except Exception as e:
            raise StorageBackendError(f"S3 下载失败: {e}") from e

    async def delete_object(self, bucket: str, key: str) -> bool:
        """从 S3 删除对象。"""
        try:
            async with self._create_client() as client:
                await client.delete_object(Bucket=bucket, Key=key)
                return True
        except Exception as e:
            raise StorageBackendError(f"S3 删除失败: {e}") from e

    async def copy_object(
        self,
        src_bucket: str,
        src_key: str,
        dst_bucket: str,
        dst_key: str,
    ) -> PutObjectResult:
        """在 S3 上复制对象。"""
        try:
            async with self._create_client() as client:
                response = await client.copy_object(
                    Bucket=dst_bucket,
                    Key=dst_key,
                    CopySource={"Bucket": src_bucket, "Key": src_key},
                )
                copy_result = response.get("CopyObjectResult", {})
                return PutObjectResult(
                    storage_path=f"{dst_bucket}/{dst_key}",
                    etag=copy_result.get("ETag", "").strip('"'),
                )
        except Exception as e:
            raise StorageBackendError(f"S3 复制失败: {e}") from e

    async def head_object(self, bucket: str, key: str) -> ObjectInfo:
        """获取 S3 对象元信息。"""
        try:
            async with self._create_client() as client:
                response = await client.head_object(Bucket=bucket, Key=key)
                return ObjectInfo(
                    key=key,
                    size=response.get("ContentLength", 0),
                    last_modified=response.get("LastModified", datetime.now(UTC)),
                    etag=response.get("ETag", "").strip('"'),
                    content_type=response.get(
                        "ContentType", "application/octet-stream"
                    ),
                    metadata=response.get("Metadata", {}),
                )
        except Exception as e:
            raise StorageBackendError(f"S3 head 失败: {e}") from e

    async def object_exists(self, bucket: str, key: str) -> bool:
        """检查 S3 对象是否存在。"""
        try:
            await self.head_object(bucket, key)
            return True
        except StorageBackendError:
            return False

    async def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000,
        continuation_token: str | None = None,
    ) -> tuple[list[ObjectInfo], str | None]:
        """列出 S3 对象。"""
        kwargs: dict[str, Any] = {
            "Bucket": bucket,
            "Prefix": prefix,
            "MaxKeys": max_keys,
        }
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token

        try:
            async with self._create_client() as client:
                response = await client.list_objects_v2(**kwargs)
                objects = []
                for item in response.get("Contents", []):
                    objects.append(
                        ObjectInfo(
                            key=item["Key"],
                            size=item.get("Size", 0),
                            last_modified=item.get("LastModified", datetime.now(UTC)),
                            etag=item.get("ETag", "").strip('"'),
                            content_type="application/octet-stream",
                        )
                    )
                next_token = response.get("NextContinuationToken")
                return objects, next_token
        except Exception as e:
            raise StorageBackendError(f"S3 列表查询失败: {e}") from e

    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> str:
        """生成 S3 预签名 URL。"""
        client_method = "get_object" if method.upper() == "GET" else "put_object"
        try:
            async with self._create_client() as client:
                url = await client.generate_presigned_url(
                    ClientMethod=client_method,
                    Params={"Bucket": bucket, "Key": key},
                    ExpiresIn=expires_in,
                )
                return url
        except Exception as e:
            raise StorageBackendError(f"S3 签名 URL 生成失败: {e}") from e

    async def create_multipart_upload(
        self,
        bucket: str,
        key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """创建 S3 分片上传。"""
        try:
            async with self._create_client() as client:
                response = await client.create_multipart_upload(
                    Bucket=bucket, Key=key, ContentType=content_type
                )
                return response["UploadId"]
        except Exception as e:
            raise StorageBackendError(f"S3 创建分片上传失败: {e}") from e

    async def upload_part(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        part_number: int,
        data: bytes,
    ) -> PartInfo:
        """上传 S3 分片。"""
        try:
            async with self._create_client() as client:
                response = await client.upload_part(
                    Bucket=bucket,
                    Key=key,
                    UploadId=upload_id,
                    PartNumber=part_number,
                    Body=data,
                )
                return PartInfo(
                    part_number=part_number,
                    etag=response["ETag"].strip('"'),
                )
        except Exception as e:
            raise StorageBackendError(f"S3 分片上传失败: {e}") from e

    async def complete_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        parts: list[PartInfo],
    ) -> PutObjectResult:
        """完成 S3 分片上传。"""
        multipart = {
            "Parts": [
                {"PartNumber": p.part_number, "ETag": p.etag}
                for p in sorted(parts, key=lambda p: p.part_number)
            ]
        }
        try:
            async with self._create_client() as client:
                response = await client.complete_multipart_upload(
                    Bucket=bucket,
                    Key=key,
                    UploadId=upload_id,
                    MultipartUpload=multipart,
                )
                return PutObjectResult(
                    storage_path=f"{bucket}/{key}",
                    etag=response.get("ETag", "").strip('"'),
                    version_id=response.get("VersionId"),
                )
        except Exception as e:
            raise StorageBackendError(f"S3 完成分片上传失败: {e}") from e

    async def abort_multipart_upload(
        self, bucket: str, key: str, upload_id: str
    ) -> None:
        """中止 S3 分片上传。"""
        try:
            async with self._create_client() as client:
                await client.abort_multipart_upload(
                    Bucket=bucket, Key=key, UploadId=upload_id
                )
        except Exception as e:
            raise StorageBackendError(f"S3 中止分片上传失败: {e}") from e

    async def create_bucket(self, bucket: str) -> None:
        """创建 S3 存储桶。"""
        try:
            async with self._create_client() as client:
                kwargs: dict[str, Any] = {"Bucket": bucket}
                if self._region != "us-east-1":
                    kwargs["CreateBucketConfiguration"] = {
                        "LocationConstraint": self._region
                    }
                await client.create_bucket(**kwargs)
        except Exception as e:
            raise StorageBackendError(f"S3 创建桶失败: {e}") from e

    async def delete_bucket(self, bucket: str) -> None:
        """删除 S3 存储桶。"""
        try:
            async with self._create_client() as client:
                await client.delete_bucket(Bucket=bucket)
        except Exception as e:
            raise StorageBackendError(f"S3 删除桶失败: {e}") from e

    async def bucket_exists(self, bucket: str) -> bool:
        """检查 S3 存储桶是否存在。"""
        try:
            async with self._create_client() as client:
                await client.head_bucket(Bucket=bucket)
                return True
        except Exception:
            return False


