"""Jinja2 沙箱模板引擎。

提供安全的模板渲染，支持变量替换、条件判断和循环。
营销邮件自动注入合规退订链接。
"""

from dataclasses import dataclass

from jinja2 import (
    Environment,
    StrictUndefined,
    TemplateSyntaxError,
    UndefinedError,
)
from jinja2.sandbox import SandboxedEnvironment

from taolib.testing.email_service.errors import TemplateRenderError
from taolib.testing.email_service.models.enums import EmailType
from taolib.testing.email_service.models.template import TemplateDocument


@dataclass
class RenderedEmail:
    """渲染后的邮件内容。"""

    subject: str
    html_body: str
    text_body: str | None = None


_UNSUBSCRIBE_HTML = """
<div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #e5e7eb;
            text-align: center; font-size: 12px; color: #6b7280;">
  <p>如果您不希望继续接收此类邮件，可以
    <a href="{url}" style="color: #3b82f6; text-decoration: underline;">点击此处退订</a>。
  </p>
  <p>If you no longer wish to receive these emails, you can
    <a href="{url}" style="color: #3b82f6; text-decoration: underline;">unsubscribe here</a>.
  </p>
</div>
"""

_UNSUBSCRIBE_TEXT = "\n---\n退订 / Unsubscribe: {url}\n"


class TemplateEngine:
    """Jinja2 沙箱模板引擎。

    使用 SandboxedEnvironment 防止模板注入攻击。
    StrictUndefined 确保缺失变量会立即报错。
    """

    def __init__(self, unsubscribe_base_url: str = "") -> None:
        """初始化。

        Args:
            unsubscribe_base_url: 退订链接的基础 URL
        """
        self._env: Environment = SandboxedEnvironment(
            undefined=StrictUndefined,
            autoescape=True,
        )
        self._unsubscribe_base_url = unsubscribe_base_url.rstrip("/")

    def render(
        self,
        template_doc: TemplateDocument,
        variables: dict,
        email_type: EmailType = EmailType.TRANSACTIONAL,
        recipient_email: str | None = None,
        unsubscribe_token: str | None = None,
    ) -> RenderedEmail:
        """渲染模板。

        Args:
            template_doc: 模板文档
            variables: 模板变量
            email_type: 邮件类型
            recipient_email: 收件人邮箱（营销邮件需要）
            unsubscribe_token: 退订令牌（营销邮件需要）

        Returns:
            渲染后的邮件内容

        Raises:
            TemplateRenderError: 模板渲染失败
        """
        try:
            subject = self._render_string(template_doc.subject_template, variables)
            html_body = self._render_string(template_doc.html_template, variables)
            text_body = None
            if template_doc.text_template:
                text_body = self._render_string(template_doc.text_template, variables)

            # 营销邮件自动注入退订链接
            if email_type == EmailType.MARKETING and recipient_email:
                html_body, text_body = self._inject_unsubscribe_link(
                    html_body, text_body, recipient_email, unsubscribe_token or ""
                )

            return RenderedEmail(
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )

        except (TemplateSyntaxError, UndefinedError) as e:
            raise TemplateRenderError(
                f"Template render failed for '{template_doc.name}': {e}"
            ) from e

    def validate_template(
        self, template_string: str, variables: dict | None = None
    ) -> list[str]:
        """验证模板语法。

        Args:
            template_string: 模板字符串
            variables: 测试变量

        Returns:
            错误列表，空列表表示有效
        """
        errors: list[str] = []
        try:
            template = self._env.from_string(template_string)
            if variables is not None:
                template.render(variables)
        except TemplateSyntaxError as e:
            errors.append(f"Syntax error: {e}")
        except UndefinedError as e:
            errors.append(f"Undefined variable: {e}")
        except Exception as e:
            errors.append(f"Render error: {e}")
        return errors

    def _render_string(self, template_string: str, variables: dict) -> str:
        """渲染单个模板字符串。"""
        template = self._env.from_string(template_string)
        return template.render(variables)

    def _inject_unsubscribe_link(
        self,
        html_body: str,
        text_body: str | None,
        email: str,
        token: str,
    ) -> tuple[str, str | None]:
        """注入退订链接。"""
        url = f"{self._unsubscribe_base_url}/unsubscribe?token={token}&email={email}"
        html_body += _UNSUBSCRIBE_HTML.format(url=url)
        if text_body:
            text_body += _UNSUBSCRIBE_TEXT.format(url=url)
        return html_body, text_body


