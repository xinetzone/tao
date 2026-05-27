"""用户管理 API 模块。

实现用户 CRUD 的 RESTful API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, status

from ...models.user import UserCreate, UserResponse, UserUpdate
from ...repository.user_repo import UserRepository
from ..dependencies import get_current_user, get_user_repo

router = APIRouter(prefix="/users", tags=["用户管理"])

USERS_API_DESCRIPTION = """
用户管理 API 提供用户的增删改查功能。

## 权限要求

- `user:read`：查看用户信息
- `user:write`：创建/更新用户
- `user:delete`：删除用户

## 用户状态

- `active`：正常状态
- `inactive`：已停用
- `locked`：已锁定
"""


@router.get(
    "",
    response_model=list[UserResponse],
    summary="获取用户列表",
    description="""
获取系统中的用户列表。

## 请求示例

```
GET /users?skip=0&limit=50
```

## 响应示例

```json
[
  {
    "id": "user_abc123",
    "username": "admin",
    "email": "admin@example.com",
    "display_name": "管理员",
    "roles": ["admin"],
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```
""",
    responses={
        200: {"description": "成功获取用户列表"},
        401: {"description": "未授权"},
    },
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """获取用户列表。"""
    users = await user_repo.list(skip=skip, limit=limit)
    return [user.to_response() for user in users]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="""
创建新用户账户。

## 请求体示例

```json
{
  "username": "newuser",
  "password": "SecurePass123!",
  "email": "newuser@example.com",
  "display_name": "新用户",
  "role_ids": ["role_editor"]
}
```

## 业务规则

- 用户名必须唯一
- 密码需满足复杂度要求（至少 8 位，包含大小写字母和数字）
- 可指定初始角色
""",
    responses={
        201: {"description": "用户创建成功"},
        400: {"description": "用户名已存在或密码不符合要求"},
        401: {"description": "未授权"},
        403: {"description": "权限不足"},
    },
)
async def create_user(
    data: UserCreate,
    current_user=Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """创建用户。"""
    try:
        user = await user_repo.create_user_with_password(
            username=data.username,
            password=data.password,
            email=data.email,
            display_name=data.display_name,
            role_ids=data.role_ids,
        )
        return user.to_response()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="获取用户详情",
    description="""
根据 ID 获取用户的详细信息。

## 路径参数

- `user_id`: 用户唯一标识符

## 响应示例

```json
{
  "id": "user_abc123",
  "username": "admin",
  "email": "admin@example.com",
  "display_name": "管理员",
  "roles": ["admin"],
  "status": "active",
  "last_login_at": "2024-01-15T10:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```
""",
    responses={
        200: {"description": "成功获取用户详情"},
        401: {"description": "未授权"},
        404: {"description": "用户不存在"},
    },
)
async def get_user(
    user_id: str,
    current_user=Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """获取用户详情。"""
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user.to_response()


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="更新用户",
    description="""
更新用户信息。

## 请求体示例

```json
{
  "display_name": "新名称",
  "email": "newemail@example.com",
  "role_ids": ["role_admin", "role_editor"]
}
```

## 可更新字段

- `display_name`: 显示名称
- `email`: 邮箱地址
- `role_ids`: 角色 ID 列表
- `status`: 用户状态
""",
    responses={
        200: {"description": "用户更新成功"},
        400: {"description": "没有提供更新数据"},
        401: {"description": "未授权"},
        403: {"description": "权限不足"},
        404: {"description": "用户不存在"},
    },
)
async def update_user(
    user_id: str,
    data: UserUpdate,
    current_user=Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """更新用户。"""
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供更新数据",
        )

    user = await user_repo.update(user_id, updates)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user.to_response()


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
    description="""
删除指定用户。

## 警告

- 删除操作不可恢复
- 用户相关的配置操作记录将保留
- 不能删除自己

## 权限要求

需要 `user:delete` 权限。
""",
    responses={
        204: {"description": "用户删除成功"},
        400: {"description": "不能删除自己"},
        401: {"description": "未授权"},
        403: {"description": "权限不足"},
        404: {"description": "用户不存在"},
    },
)
async def delete_user(
    user_id: str,
    current_user=Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """删除用户。"""
    deleted = await user_repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
