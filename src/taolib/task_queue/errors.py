"""任务队列自定义异常。

定义任务队列系统中使用的异常层次结构。
"""


class TaskQueueError(Exception):
    """所有任务队列错误的基类。"""

    pass


class TaskNotFoundError(TaskQueueError):
    """任务不存在。"""

    pass


class TaskAlreadyExistsError(TaskQueueError):
    """幂等键冲突，任务已存在。"""

    pass


class TaskHandlerNotFoundError(TaskQueueError):
    """指定任务类型没有注册处理器。"""

    pass


class TaskExecutionError(TaskQueueError):
    """任务处理器执行时抛出不可恢复的错误。"""

    pass


class TaskQueueConnectionError(TaskQueueError):
    """Redis 连接失败。"""

    pass


class TaskMaxRetriesExceededError(TaskQueueError):
    """任务重试次数已达上限。"""

    pass
