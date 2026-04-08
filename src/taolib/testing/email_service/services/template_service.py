"""模板管理服务。

提供模板的 CRUD 操作和渲染功能。
"""

import uuid
from datetime import UTC, datetime

from taolib.testing.email_service.errors import TemplateNotFoundError
from taolib.testing.email_service.models.enums import EmailType
from taolib.testing.email_service.models.template import (
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)
from taolib.testing.email_service.repository.template_repo import TemplateRepository
from taolib.testing.email_service.template.engine import RenderedEmail, TemplateEngine


class TemplateService:
    """模板管理服务。"""

    def __init__(
        self,
        template_repo: TemplateRepository,
        engine: TemplateEngine,
    ) -> None:
        """初始化。

        Args:
            template_repo: 模板 Repository
            engine: 模板引擎
        """
        self._repo = template_repo
        self._engine = engine

    async def create_template(self, data: TemplateCreate) -> TemplateResponse:
        """创建模板。"""
        doc_dict = {
            "_id": str(uuid.uuid4()),
            **data.model_dump(),
            "is_active": True,
            "version": 1,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        doc = await self._repo.create(doc_dict)
        return doc.to_response()

    async def update_template(
        self, template_id: str, data: TemplateUpdate
    ) -> TemplateResponse | None:
        """更新模板。"""
        updates = data.model_dump(exclude_none=True)
        if not updates:
            existing = await self._repo.get_by_id(template_id)
            return existing.to_response() if existing else None

        updates["updated_at"] = datetime.now(UTC)
        # 递增版本号
        existing = await self._repo.get_by_id(template_id)
        if existing:
            updates["version"] = existing.version + 1

        doc = await self._repo.update(template_id, updates)
        return doc.to_response() if doc else None

    async def get_template(self, template_id: str) -> TemplateResponse | None:
        """获取模板。"""
        doc = await self._repo.get_by_id(template_id)
        return doc.to_response() if doc else None

    async def get_template_by_name(self, name: str) -> TemplateResponse | None:
        """按名称获取模板。"""
        doc = await self._repo.find_by_name(name)
        return doc.to_response() if doc else None

    async def list_templates(
        self,
        email_type: EmailType | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TemplateResponse]:
        """查询模板列表。"""
        filters: dict = {}
        if email_type:
            filters["email_type"] = str(email_type)
        if is_active is not None:
            filters["is_active"] = is_active
        docs = await self._repo.list(
            filters=filters if filters else None,
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)],
        )
        return [d.to_response() for d in docs]

    async def delete_template(self, template_id: str) -> bool:
        """删除模板。"""
        return await self._repo.delete(template_id)

    async def render_template(
        self,
        template_id: str,
        variables: dict,
        email_type: EmailType = EmailType.TRANSACTIONAL,
        recipient_email: str | None = None,
        unsubscribe_token: str | None = None,
    ) -> RenderedEmail:
        """渲染模板。

        Args:
            template_id: 模板 ID
            variables: 模板变量
            email_type: 邮件类型
            recipient_email: 收件人邮箱
            unsubscribe_token: 退订令牌

        Returns:
            渲染后的邮件内容

        Raises:
            TemplateNotFoundError: 模板不存在
        """
        doc = await self._repo.get_by_id(template_id)
        if doc is None:
            raise TemplateNotFoundError(f"Template not found: {template_id}")

        return self._engine.render(
            template_doc=doc,
            variables=variables,
            email_type=email_type,
            recipient_email=recipient_email,
            unsubscribe_token=unsubscribe_token,
        )


