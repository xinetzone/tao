# 最佳实践

## 使用 `typing.Self` 替代 `TypeVar` 进行自引用类型注解

`typing.Self`（Python 3.11+ 引入，PEP 673）用于表示"当前类的实例类型"，是对旧式 `TypeVar` 自引用模式的简洁替代。在方法返回 `self` 或通过 `classmethod` 返回当前类实例时，应优先使用 `Self`。

### 适用场景
- 链式调用 (Builder/Fluent 模式)
- 工厂方法 / classmethod
- 上下文管理器 `__enter__`
- 子类继承中的类型精确推断