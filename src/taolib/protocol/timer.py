import sys
from typing import Protocol

# 新增类型别名提高可读性
if sys.version >= "3.12":
    type TimeDelta = float
else:
    TimeDelta = float

class Timer(Protocol):
    """计时器抽象接口 (支持 isinstancel 检查)"""
    
    def start(self) -> None:
        """启动计时器
        
        Raises:
            RuntimeError: 当计时器已经启动时抛出
        """
        ...
    
    def stop(self) -> TimeDelta:
        """停止计时并返回持续时间
        
        Returns:
            TimeDelta: 最后一次计时的时间差（单位：秒）
            
        Raises:
            RuntimeError: 当计时器未启动时抛出
        """
        ...
    
    def avg(self) -> TimeDelta:
        """计算平均耗时
        
        Returns:
            TimeDelta: 所有记录时间的平均值
        """
        ...
    
    def sum(self) -> TimeDelta:
        """计算总耗时
        
        Returns:
            TimeDelta: 所有记录时间的总和
        """
        ...
    
    def cumsum(self) -> list[TimeDelta]:
        """生成累计耗时序列
        
        Returns:
            list[TimeDelta]: 按记录顺序生成的累计时间列表
        """
        ...