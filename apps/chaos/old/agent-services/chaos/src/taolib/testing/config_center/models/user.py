"""用户与角色数据模型模块。

定义用户、角色和权限相关的 Pydantic 模型。
"""

from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, Field

from .enums import Environment


class Permission(BaseModel):
    """权限模型。"""

    resource: str = Field(..., description="资源类型", max_length=100)
    actions: list[str] = Field(..., description="允许的操作列表")


class RoleBase(BaseModel):
    """角色基础模型。"""

    name: str = Field(..., description="角色名称", min_length=1, max_length=100)
    description: str = Field(default="", description="角色描述", max_length=500)
    permissions: list[Permission] = Field(default_factory=list, description="权限列表")
    environment_scope: list[Environment] | None = Field(
        default=None, description="环境作用域（None 表示全部）"
    )
    service_scope: list[str] | None = Field(
        default=None, description="服务作用域（None 表示全部）"
    )


class RoleCreate(RoleBase):
    """创建角色请求模型。"""

    pass


class RoleUpdate(BaseModel):
    """更新角色请求模型。"""

    description: str | None = Field(
        default=None, description="角色描述", max_length=500
    )
    permissions: list[Permission] | None = Field(default=None, description="权限列表")
    environment_scope: list[Environment] | None = Field(
        default=None, description="环境作用域"
    )
    service_scope: list[str] | None = Field(default=None, description="服务作用域")


class RoleResponse(RoleBase):
    """角色响应模型。"""

    id: str = Field(..., description="角色 ID")
    is_system: bool = Field(default=False, description="是否系统内置角色")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    model_config = {"from_attributes": True}


class RoleDocument(RoleBase):
    """MongoDB 角色文档模型。"""

    id: str = Field(default="", alias="_id", description="MongoDB ObjectId")
    is_system: bool = Field(default=False, description="是否系统内置角色")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="最后更新时间"
    )

    model_config = {"populate_by_name": True}

    def to_response(self) -> RoleResponse:
        """转换为响应模型。"""
        return RoleResponse(
            id=self.id,
            name=self.name,
            description=self.description,
            permissions=self.permissions,
            environment_scope=self.environment_scope,
            service_scope=self.service_scope,
            is_system=self.is_system,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class UserBase(BaseModel):
    """用户基础模型。"""

    username: str = Field(..., description="用户名", min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, description="邮箱地址")
    display_name: str = Field(default="", description="显示名称", max_length=255)
    is_active: bool = Field(default=True, description="是否激活")


class UserCreate(UserBase):
    """创建用户请求模型。"""

    password: str = Field(..., description="密码", min_length=6)
    role_ids: list[str] = Field(default_factory=list, description="关联角色 IDs")


class UserUpdate(BaseModel):
    """更新用户请求模型。"""

    email: EmailStr | None = Field(default=None, description="邮箱地址")
    display_name: str | None = Field(
        default=None, description="显示名称", max_length=255
    )
    is_active: bool | None = Field(default=None, description="是否激活")
    role_ids: list[str] | None = Field(default=None, description="关联角色 IDs")


class UserResponse(UserBase):
    """用户响应模型。"""

    id: str = Field(..., description="用户 ID")
    role_ids: list[str] = Field(default_factory=list, description="关联角色 IDs")
    last_login: datetime | None = Field(default=None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    model_config = {"from_attributes": True}


class UserDocument(UserBase):
    """MongoDB 用户文档模型。"""

    id: str = Field(default="", alias="_id", description="MongoDB ObjectId")
    password_hash: str = Field(..., description="密码哈希")
    role_ids: list[str] = Field(default_factory=list, description="关联角色 IDs")
    last_login: datetime | None = Field(default=None, description="最后登录时间")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="最后更新时间"
    )

    model_config = {"populate_by_name": True}

    def to_response(self) -> UserResponse:
        """转换为响应模型（不包含密码）。"""
        return UserResponse(
            id=self.id,
            username=self.username,
            email=self.email,
            display_name=self.display_name,
            is_active=self.is_active,
            role_ids=self.role_ids,
            last_login=self.last_login,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
