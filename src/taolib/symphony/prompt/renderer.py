"""Jinja2 严格模板渲染。

用于渲染用户 WORKFLOW.md 中的提示词模板，
使用 StrictUndefined 模式确保未知变量不会静默失败。
"""

import logging
from typing import Any

from jinja2 import Environment, StrictUndefined, TemplateSyntaxError

from ..errors import PromptError

__all__ = ["render_prompt"]

logger = logging.getLogger(__name__)

_env = Environment(undefined=StrictUndefined)


def render_prompt(
    template_str: str,
    issue: Any,
    attempt: int | None = None,
) -> str:
    """渲染用户模板（Jinja2 strict 模式）。

    将 Issue 数据注入模板，严格模式确保引用未定义变量时
    抛出异常而非静默渲染为空字符串。

    Args:
        template_str: Jinja2 模板字符串。
        issue: Issue 对象（需支持 ``model_dump()`` 方法）。
        attempt: 当前尝试序号。

    Returns:
        渲染后的提示词字符串。

    Raises:
        PromptError: 模板语法错误或渲染错误。
    """
    try:
        tmpl = _env.from_string(template_str)
    except TemplateSyntaxError as e:
        raise PromptError("template_parse_error", str(e)) from e

    # 构建模板上下文
    context: dict[str, Any] = {"attempt": attempt}
    if hasattr(issue, "model_dump"):
        context["issue"] = issue.model_dump()
    elif isinstance(issue, dict):
        context["issue"] = issue
    else:
        context["issue"] = {"identifier": str(issue)}

    try:
        return tmpl.render(context)
    except Exception as e:
        raise PromptError("template_render_error", str(e)) from e
