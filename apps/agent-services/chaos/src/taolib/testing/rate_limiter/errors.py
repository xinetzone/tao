"""Rate limiter custom exceptions."""

import time


class RateLimitExceededError(Exception):
    """限流阈值超出异常。

    当请求频率超过配置的限流阈值时抛出。
    """

    def __init__(
        self,
        *,
        limit: int,
        window_seconds: int,
        retry_after: int,
        identifier: str,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.retry_after = retry_after
        self.identifier = identifier
        self.reset_timestamp = time.time() + retry_after
        message = (
            f"Rate limit exceeded for '{identifier}': "
            f"{limit} requests per {window_seconds}s. "
            f"Retry after {retry_after}s."
        )
        super().__init__(message)


