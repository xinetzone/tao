"""模板 CRUD 端点。"""

from fastapi import APIRouter, HTTPException, Query, Request

from taolib.testing.email_service.models.enums import EmailType
from taolib.testing.email_service.models.template import (
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)

router = APIRouter()


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(data: TemplateCreate, request: Request):
    """创建模板。"""
    return await request.app.state.template_service.create_template(data)


@router.get("", response_model=list[TemplateResponse])
async def list_templates(
    request: Request,
    email_type: EmailType | None = Query(None),
    is_active: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """查询模板列表。"""
    return await request.app.state.template_service.list_templates(
        email_type=email_type, is_active=is_active, skip=skip, limit=limit
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str, request: Request):
    """获取模板详情。"""
    result = await request.app.state.template_service.get_template(template_id)
    if result is None:
        raise HTTPException(404, "Template not found")
    return result


@router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: str, data: TemplateUpdate, request: Request):
    """更新模板。"""
    result = await request.app.state.template_service.update_template(template_id, data)
    if result is None:
        raise HTTPException(404, "Template not found")
    return result


@router.delete("/{template_id}")
async def delete_template(template_id: str, request: Request):
    """删除模板。"""
    deleted = await request.app.state.template_service.delete_template(template_id)
    if not deleted:
        raise HTTPException(404, "Template not found")
    return {"deleted": True}


@router.post("/{template_id}/preview")
async def preview_template(
    template_id: str,
    variables: dict,
    request: Request,
):
    """预览模板渲染结果。"""
    from taolib.testing.email_service.errors import TemplateNotFoundError, TemplateRenderError

    try:
        rendered = await request.app.state.template_service.render_template(
            template_id=template_id, variables=variables
        )
        return {
            "subject": rendered.subject,
            "html_body": rendered.html_body,
            "text_body": rendered.text_body,
        }
    except TemplateNotFoundError:
        raise HTTPException(404, "Template not found")
    except TemplateRenderError as e:
        raise HTTPException(422, str(e))


