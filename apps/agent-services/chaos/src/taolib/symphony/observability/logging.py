"""结构化日志配置。

基于 structlog，支持 JSON 和 key=value 两种输出格式。
所有问题相关日志自动携带 issue_id、issue_identifier 上下文。
"""

import logging
import sys

import structlog


def configure_logging(
    level: str = "info",
    format: str = "json",
    output: str = "stderr",
) -> None:
    """配置 structlog。

    Args:
        level: 日志级别，如 "debug"、"info"、"warning"、"error"。
        format: 输出格式，"json" 或 "console"。
        output: 输出目标，"stderr" 或 "stdout"。
    """
    processors: list[object] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    stream = sys.stderr if output == "stderr" else sys.stdout

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=stream),
        cache_logger_on_first_use=True,
    )


def bind_issue_context(issue_id: str, identifier: str) -> None:
    """绑定 issue 上下文到当前协程。

    之后的日志调用会自动携带 issue_id 和 issue_identifier 字段。

    Args:
        issue_id: 问题内部 ID。
        identifier: 人类可读的问题标识（如 "PROJ-123"）。
    """
    structlog.contextvars.bind_contextvars(
        issue_id=issue_id,
        issue_identifier=identifier,
    )


def clear_issue_context() -> None:
    """清除 issue 上下文。"""
    structlog.contextvars.unbind_contextvars("issue_id", "issue_identifier")


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """获取绑定名称的结构化日志器。

    Args:
        name: 日志器名称，通常为模块名。

    Returns:
        配置好的 structlog BoundLogger 实例。
    """
    return structlog.get_logger(name)
