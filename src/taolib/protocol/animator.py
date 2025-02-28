import sys
from typing import Protocol, Iterable

# 新增类型别名提高可读性
if sys.version >= "3.12":
    type Number = float | int
else:
    Number = float | int

class Animator(Protocol):
    """协议类定义动画系统接口"""
    def add(self, x: Number|Iterable[Number], y: Number|Iterable[Number]) -> None:
        """添加关键帧数据
        
        Args:
            x: 时间序列（支持单个值或可迭代序列）
            y: 属性值序列（需与x长度保持一致）
        """
        ...
