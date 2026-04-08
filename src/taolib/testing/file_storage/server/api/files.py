"""文件端点。"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from taolib.testing.file_storage.models.enums import AccessLevel, MediaType
from taolib.testing.file_storage.models.file import FileMetadataResponse, FileMetadataUpdate
from taolib.testing.file_storage.services.file_service import FileService

router = APIRouter()

FILES_API_DESCRIPTION = """
文件存储 API 提供文件上传、下载和管理功能。

## 功能特性

- **多后端支持**：本地存储、Amazon S3
- **分片上传**：支持大文件分片上传
- **版本控制**：文件版本管理
- **缩略图**：自动生成图片缩略图
- **签名 URL**：生成临时访问链接
- **访问控制**：私有/公开访问级别

## 存储桶（Bucket）

所有文件必须存储在存储桶中，每个存储桶可以配置：
- 存储后端类型
- 访问权限
- 生命周期规则
"""


@router.get(
    "",
    response_model=list[FileMetadataResponse],
    summary="列出文件",
    description="""
列出文件，支持多种过滤条件。

## 查询参数

- `bucket_id`: 存储桶 ID（可选）
- `prefix`: 路径前缀过滤（可选）
- `tags`: 标签过滤，逗号分隔（可选）
- `media_type`: 媒体类型过滤（可选）
- `skip`: 跳过记录数
- `limit`: 返回数量

## 响应示例

```json
[
  {
    "id": "file_abc123",
    "bucket_id": "bucket_001",
    "object_key": "images/avatar.png",
    "filename": "avatar.png",
    "content_type": "image/png",
    "size": 1024,
    "access_level": "public",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```
""",
    responses={
        200: {"description": "成功获取文件列表"}
    },
)
async def list_files(
    bucket_id: str | None = Query(None),
    prefix: str | None = Query(None),
    tags: str | None = Query(None),
    media_type: MediaType | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = 100, ge=1, le=1000,
    file_service: FileService = Depends(),
):
    """列出文件（支持多种过滤条件）。"""
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    return await file_service.list_files(
        bucket_id=bucket_id,
        prefix=prefix,
        tags=tag_list,
        media_type=media_type.value if media_type else None,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/upload",
    response_model=FileMetadataResponse,
    summary="简单上传",
    description="""
简单文件上传，适用于小文件。

## 请求参数

- `file`: 上传的文件
- `bucket_id`: 目标桶 ID（必填）
- `object_key`: 对象键（桶内路径，必填）
- `access_level`: 访问级别（默认 private）

## 限制

- 单个文件最大 10MB
- 超过 10MB 请使用分片上传

## 响应示例

```json
{
  "id": "file_abc123",
  "bucket_id": "bucket_001",
  "object_key": "images/avatar.png",
  "size": 1024,
  "access_level": "public"
}
```
""",
    responses={
        201: {"description": "文件上传成功"},
        400: {"description": "文件过大或参数错误"},
        404: {"description": "存储桶不存在"},
    },
)
async def upload_file(
    file: UploadFile,
    bucket_id: str = Query(..., description="目标桶 ID"),
    object_key: str = Query(..., description="对象键（桶内路径）"),
    access_level: AccessLevel = Query(AccessLevel.PRIVATE, description="访问级别"),
    file_service: FileService = Depends(),
):
    """简单文件上传（适用于小文件）。"""
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    return await file_service.upload_file(
        bucket_id=bucket_id,
        object_key=object_key,
        data=content,
        filename=file.filename or "unknown",
        content_type=content_type,
        access_level=access_level,
    )


@router.get(
    "/{file_id}",
    response_model=FileMetadataResponse,
    summary="获取文件元数据",
    description="""
获取文件的元数据信息。

## 路径参数

- `file_id`: 文件唯一标识符

## 响应示例

```json
{
  "id": "file_abc123",
  "bucket_id": "bucket_001",
  "object_key": "images/avatar.png",
  "filename": "avatar.png",
  "content_type": "image/png",
  "size": 1024,
  "access_level": "public",
  "created_at": "2024-01-15T10:30:00Z"
}
```
""",
    responses={
        200: {"description": "成功获取文件元数据"},
        404: {"description": "文件不存在"},
    },
)
async def get_file(
    file_id: str,
    file_service: FileService = Depends(),
):
    """获取文件元数据。"""
    file = await file_service.get_file(file_id)
    if file is None:
        raise HTTPException(status_code=404, detail="文件不存在")
    return file


@router.patch(
    "/{file_id}",
    response_model=FileMetadataResponse,
    summary="更新文件元数据",
    description="""
更新文件的元数据（tags、description、access_level）。

## 请求体示例

```json
{
  "tags": ["profile", "avatar"],
  "description": "用户头像",
  "access_level": "public"
}
```

## 响应示例

```json
{
  "id": "file_abc123",
  "tags": ["profile", "avatar"],
  "description": "用户头像",
  "access_level": "public"
}
```
""",
    responses={
        200: {"description": "文件元数据更新成功"},
        404: {"description": "文件不存在"},
    },
)
async def update_file(
    file_id: str,
    data: FileMetadataUpdate,
    file_service: FileService = Depends(),
):
    """更新文件元数据（tags、description、access_level）。"""
    file = await file_service.update_metadata(file_id, data)
    if file is None:
        raise HTTPException(status_code=404, detail="文件不存在")
    return file


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除文件",
    description="""
删除文件及其所有版本。

## 警告

- 删除操作不可恢复
- 所有版本将被删除
- 如果文件是公开的，删除后无法访问

## 响应

HTTP 204 No Content

## 错误码

- 400: 删除失败
- 404: 文件不存在
""",
    responses={
        204: {"description": "文件删除成功"},
        400: {"description": "删除失败"},
        404: {"description": "文件不存在"},
    },
)
async def delete_file(
    file_id: str,
    file_service: FileService = Depends(),
):
    """删除文件。"""
    try:
        await file_service.delete_file(file_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{file_id}/download",
    summary="下载文件",
    description="""
下载文件（流式）。

## 路径参数

- `file_id`: 文件唯一标识符

## 响应

返回文件流，Content-Type 为文件的实际类型。

## 错误码

- 404: 文件不存在
""",
    responses={
        200: {"description": "文件流"},
        404: {"description": "文件不存在"},
    },
)
async def download_file(
    file_id: str,
    file_service: FileService = Depends(),
):
    """下载文件（流式）。"""
    stream = await file_service.download_file(file_id)
    return StreamingResponse(stream, media_type="application/octet-stream")


@router.get(
    "/{file_id}/url",
    summary="获取文件访问 URL",
    description="""
获取文件访问 URL（签名 URL）。

## 路径参数

- `file_id`: 文件唯一标识符

## 查询参数

- `expires_in`: URL 有效期（默认 3600 秒）

## 响应示例

```json
{
  "url": "https://storage.example.com/signed-url-here"
}
```

## 错误码

- 404: 文件不存在
""",
    responses={
        200: {"description": "文件访问 URL"},
        404: {"description": "文件不存在"},
    },
)
async def get_file_url(
    file_id: str,
    expires_in: int = Query(3600, ge=60),
    file_service: FileService = Depends(),
):
    """获取文件访问 URL。"""
    try:
        url = await file_service.get_file_url(file_id, expires_in)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


