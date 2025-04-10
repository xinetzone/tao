from dataclasses import dataclass
import numpy as np

# np.int15 = np.dtype([("int15", "b", 15)]) # 等价于 np.int15 = np.dtype([("int15", "i1", 15)])
np.int8e = np.dtype([("int8e", np.int8, 16)]) # 针对深度可分离卷积的扩展权重

@dataclass(eq=True, order=True)
class TensorType:
    shape: tuple[int]
    dtype: str
    name: str = "data"

    def __post_init__(self):
        if self.dtype == "int8e":
            self.dtype = np.int8e

    @property
    def empty(self):
        '''空的输出张量'''
        return np.empty(shape=self.shape,
                        dtype=self.dtype)

    @property
    def nbytes(self):
        '''输出张量的存储字节数'''
        return self.empty.nbytes

    @property
    def nelement(self):
        '''输出张量的元素个数'''
        return self.empty.size

    def weak_eq(self, other):
        """不考虑对名称的依赖"""
        assert_shape = self.shape == other.shape
        assert_dtype = self.dtype == other.dtype
        return assert_shape and assert_dtype
