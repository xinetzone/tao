"""内部提示词模板（PEP 750 t-string）。

用于续运提示词和默认提示词构建，不使用 Jinja2。
PEP 750 (Python 3.14+) t-string 语法提供类型安全的模板插值，
无需外部模板引擎。
"""

from string.templatelib import Interpolation, Template

__all__ = ["build_continuation_prompt", "build_default_prompt"]


def build_continuation_prompt(
    identifier: str,
    title: str,
    turn: int,
    max_turns: int,
) -> str:
    """构建续运轮次提示词。

    当 Codex 智能体需要继续上一轮未完成的工作时，
    使用此模板生成引导性提示词。

    Args:
        identifier: Issue 标识符。
        title: Issue 标题。
        turn: 当前轮次号。
        max_turns: 最大轮次数。

    Returns:
        续运提示词字符串。
    """
    template = t"Continue working on {identifier}: {title}. This is turn {turn}/{max_turns}. Review progress and continue."
    return _render(template)


def build_default_prompt(identifier: str, title: str) -> str:
    """构建默认提示词（无用户模板时的回退）。

    当用户未提供 WORKFLOW.md 模板时，
    使用此模板生成基本的提示词。

    Args:
        identifier: Issue 标识符。
        title: Issue 标题。

    Returns:
        默认提示词字符串。
    """
    template = t"You are working on a Linear issue. Issue: {identifier} - {title}"
    return _render(template)


def _render(template: Template) -> str:
    """渲染 PEP 750 t-string 模板。

    遍历模板的各个部分，将插值替换为字符串值，
    文本部分直接拼接。

    Args:
        template: PEP 750 Template 对象。

    Returns:
        渲染后的字符串。
    """
    parts: list[str] = []
    for part in template:
        if isinstance(part, Interpolation):
            parts.append(str(part.value))
        else:
            parts.append(part)
    return "".join(parts)
