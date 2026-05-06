"""Tracker 异常层次 — Linear API 专用错误类型。

所有 Linear 相关异常均继承自 ``TrackerError``（来自
:mod:`taolib.symphony.errors`），与 Symphony 其余子系统共享同一基类。
"""

from taolib.symphony.errors import TrackerError


class LinearError(TrackerError):
    """所有 Linear API 相关错误的基类。

    便于调用方一次性捕获全部 Linear 异常，也可按子类精细处理。
    """

    pass


class LinearAPIRequestError(LinearError):
    """网络 / 传输层错误。

    在 HTTP 请求本身无法发出或连接中断时抛出，
    例如 DNS 解析失败、连接超时、TLS 握手错误等。
    """

    pass


class LinearAPIStatusError(LinearError):
    """非 2xx 响应状态码。

    携带 ``status_code`` 属性以方便调用方区分 4xx / 5xx。
    """

    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class LinearGraphQLError(LinearError):
    """GraphQL 响应中 ``errors`` 字段非空。

    Linear API 在业务层校验失败时返回此类错误，
    例如字段不存在、权限不足、变量类型不匹配等。
    """

    def __init__(self, message: str, *, errors: list[dict]) -> None:
        super().__init__(message)
        self.errors = errors


class LinearMissingCursorError(LinearError):
    """分页响应缺少 ``endCursor``。

    当 Linear 返回 ``hasNextPage=True`` 却未提供 ``endCursor``
    时抛出，表示分页完整性受损，无法继续翻页。
    """

    pass
