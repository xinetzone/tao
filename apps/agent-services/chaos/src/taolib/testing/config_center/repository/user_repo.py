"""用户 Repository 模块。

提供用户文档的 MongoDB 操作实现，包含密码哈希处理。
"""

from passlib.hash import bcrypt

from ..models.user import UserDocument
from .base import AsyncRepository


class UserRepository(AsyncRepository[UserDocument]):
    """用户 Repository 实现。"""

    def __init__(self, collection) -> None:
        """初始化用户 Repository。

        Args:
            collection: MongoDB users 集合对象
        """
        super().__init__(collection, UserDocument)

    async def find_by_username(self, username: str) -> UserDocument | None:
        """根据用户名查找用户。

        Args:
            username: 用户名

        Returns:
            用户文档实例，如果不存在则返回 None
        """
        document = await self._collection.find_one({"username": username})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return UserDocument(**document)

    async def find_by_email(self, email: str) -> UserDocument | None:
        """根据邮箱查找用户。

        Args:
            email: 邮箱地址

        Returns:
            用户文档实例，如果不存在则返回 None
        """
        document = await self._collection.find_one({"email": email})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return UserDocument(**document)

    async def create_user_with_password(
        self,
        username: str,
        password: str,
        email: str | None = None,
        display_name: str = "",
        role_ids: list[str] | None = None,
    ) -> UserDocument:
        """创建用户并哈希密码。

        Args:
            username: 用户名
            password: 明文密码
            email: 邮箱地址
            display_name: 显示名称
            role_ids: 角色 IDs

        Returns:
            创建的用户文档实例

        Raises:
            ValueError: 如果用户名已存在
        """
        existing = await self.find_by_username(username)
        if existing is not None:
            raise ValueError(f"用户名已存在：{username}")

        password_hash = bcrypt.hash(password)
        document = {
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "display_name": display_name,
            "role_ids": role_ids or [],
            "is_active": True,
        }
        return await self.create(document)

    async def verify_password(self, user_id: str, password: str) -> bool:
        """验证用户密码。

        Args:
            user_id: 用户 ID
            password: 明文密码

        Returns:
            密码是否正确
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return False
        return bcrypt.verify(password, user.password_hash)

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index([("username", 1)], unique=True)
        await self._collection.create_index([("email", 1)], unique=True, sparse=True)

    async def get_user_roles(self, user_id: str, role_collection) -> list[dict]:
        """获取用户的角色列表。

        Args:
            user_id: 用户 ID
            role_collection: MongoDB roles 集合对象

        Returns:
            角色列表，每个角色包含 id、name、permissions 等字段
        """
        user = await self.get_by_id(user_id)
        if user is None or not user.role_ids:
            return []

        from bson.objectid import ObjectId

        role_ids = [ObjectId(rid) for rid in user.role_ids]
        cursor = role_collection.find({"_id": {"$in": role_ids}})
        roles = await cursor.to_list(length=None)

        # 转换 ObjectId 为字符串
        for role in roles:
            role["_id"] = str(role["_id"])

        return roles


