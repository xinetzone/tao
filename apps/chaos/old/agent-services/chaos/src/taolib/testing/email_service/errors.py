"""邮件服务自定义异常模块。

定义邮件服务系统的异常层级结构。
"""


class EmailServiceError(Exception):
    """邮件服务基础异常。"""

    pass


class EmailNotFoundError(EmailServiceError):
    """邮件记录未找到。"""

    pass


class TemplateNotFoundError(EmailServiceError):
    """模板未找到。"""

    pass


class TemplateRenderError(EmailServiceError):
    """模板渲染失败。"""

    pass


class ProviderError(EmailServiceError):
    """邮件提供商通信错误。"""

    pass


class AllProvidersFailedError(ProviderError):
    """所有提供商均发送失败。"""

    def __init__(self, errors: list[tuple[str, str]] | None = None) -> None:
        """初始化。

        Args:
            errors: (提供商名称, 错误信息) 列表
        """
        self.errors = errors or []
        details = "; ".join(f"{name}: {msg}" for name, msg in self.errors)
        super().__init__(
            f"All providers failed: {details}" if details else "All providers failed"
        )


class QueueError(EmailServiceError):
    """队列操作错误。"""

    pass


class SubscriptionError(EmailServiceError):
    """订阅操作错误。"""

    pass
