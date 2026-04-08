"""角色管理 API 模块。

实现角色 CRUD 的 RESTful API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, status

from ...models.user import RoleCreate, RoleResponse, RoleUpdate
from ...repository.role_repo import RoleRepository
from ..dependencies import get_current_user, get_role_repo

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.get("", response_model=list[RoleResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    role_repo: RoleRepository = Depends(get_role_repo),
    current_user=Depends(get_current_user),
) -> list[RoleResponse]:
    """获取角色列表。

    Args:
        skip: 跳过记录数
        limit: 限制记录数
        role_repo: 角色 Repository
        current_user: 当前用户

    Returns:
        角色列表
    """
    roles = await role_repo.list(skip=skip, limit=limit)
    return [RoleResponse(**role.model_dump()) for role in roles]


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    role_repo: RoleRepository = Depends(get_role_repo),
    current_user=Depends(get_current_user),
) -> RoleResponse:
    """创建角色。

    Args:
        data: 角色创建数据
        role_repo: 角色 Repository
        current_user: 当前用户

    Returns:
        创建的角色
    """
    # 检查角色名是否已存在
    existing = await role_repo.find_by_name(data.name)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"角色名称已存在：{data.name}",
        )

    document = {
        "name": data.name,
        "description": data.description or "",
        "permissions": data.permissions or [],
        "environment_access": data.environment_access or [],
        "is_system": False,
    }
    role = await role_repo.create(document)
    return RoleResponse(**role.model_dump())


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    role_repo: RoleRepository = Depends(get_role_repo),
    current_user=Depends(get_current_user),
) -> RoleResponse:
    """获取角色详情。

    Args:
        role_id: 角色 ID
        role_repo: 角色 Repository
        current_user: 当前用户

    Returns:
        角色详情
    """
    role = await role_repo.get_by_id(role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在",
        )
    return RoleResponse(**role.model_dump())


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    data: RoleUpdate,
    role_repo: RoleRepository = Depends(get_role_repo),
    current_user=Depends(get_current_user),
) -> RoleResponse:
    """更新角色。

    Args:
        role_id: 角色 ID
        data: 角色更新数据
        role_repo: 角色 Repository
        current_user: 当前用户

    Returns:
        更新后的角色
    """
    role = await role_repo.get_by_id(role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在",
        )

    # 系统角色不允许修改
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="系统角色不允许修改",
        )

    updates = data.model_dump(exclude_unset=True)
    updated_role = await role_repo.update(role_id, updates)
    if updated_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色更新失败",
        )
    return RoleResponse(**updated_role.model_dump())


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    role_repo: RoleRepository = Depends(get_role_repo),
    current_user=Depends(get_current_user),
) -> None:
    """删除角色。

    Args:
        role_id: 角色 ID
        role_repo: 角色 Repository
        current_user: 当前用户

    Raises:
        HTTPException: 如果角色不存在或为系统角色
    """
    role = await role_repo.get_by_id(role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在",
        )

    # 系统角色不允许删除
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="系统角色不允许删除",
        )

    await role_repo.delete(role_id)


