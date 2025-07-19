import time

class Timer:
    """高精度计时工具（支持微秒级测量）

    Attributes:
        times (list[float]): 存储所有计时结果的列表（单位：秒）
        _tik (float): 当前计时起点的时间戳
    """

    def __init__(self) -> None:
        self.times: list[float] = []
        self._tik: float = 0.0
        self.start()  # 自动开始首次计时

    def start(self) -> None:
        """开始新的计时周期"""
        self._tik = time.perf_counter()  # 使用高精度的计时器

    def stop(self) -> float:
        """停止计时并返回本次持续时间
        
        Returns:
            float: 最后一次计时的持续时间（秒）
            
        Raises:
            RuntimeError: 如果未调用 start() 直接调用 stop()
        """
        if self._tik == 0.0:
            raise RuntimeError("Timer not started")
        delta = time.perf_counter() - self._tik
        self.times.append(delta)
        self._tik = 0.0  # 重置计时标记
        return delta

    def avg(self) -> float:
        """计算平均耗时"""
        return sum(self.times) / len(self.times) if self.times else 0.0

    def sum(self) -> float:
        """计算总耗时"""
        return sum(self.times)

    def cumsum(self) -> list[float]:
        """生成累计耗时序列"""
        cumulative = 0.0
        # 高效纯Python实现，时间复杂度为 O(n)
        return [cumulative := cumulative + t for t in self.times]
