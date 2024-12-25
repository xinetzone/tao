from __future__ import annotations
from dataclasses import dataclass
from contextlib import ContextDecorator
import logging
import time
import numpy as np

@dataclass
class TimerContext(ContextDecorator):
    """追踪上下文信息

    Args:
        name: 计时器名称
    """
    name: str = "Timer"

    def __post_init__(self):
        # 记录开始时间
        self._times = []  # 记录时间戳
        self.times = []  # 记录时间段

    def __enter__(self):
        logging.debug(f"Entering {self.name}.")
        self._times.append(time.time())
        return self

    @property
    def runtime(self):
        return (self._times[-1] - self._times[-2]) * 1000

    def __exit__(self, *exc_details):
        self._times.append(time.time())
        self.times.append(self.runtime)
        logging.debug(f"Run time: {self.times[-1]:.7g} ms.")
        logging.debug(f"Exiting {self.name}.")
        return False

    def reset(self):
        """重置记录"""
        self._times = []
        self.times = []

    def __len__(self):
        """返回运行次数"""
        return len(self.times)

    def sum(self):
        """返回时间总和"""
        return sum(self.times)

    def avg(self):
        """返回平均时间"""
        return self.sum() / len(self)

    def cumsum(self):
        """返回累计时间"""
        return np.array(self.times).cumsum().tolist()
