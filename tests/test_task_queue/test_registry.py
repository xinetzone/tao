"""任务处理器注册表测试。

覆盖 TaskHandlerRegistry 的注册、查找、装饰器和类型判断。
"""

from taolib.task_queue.worker.registry import (
    TaskHandlerRegistry,
    get_default_registry,
    task_handler,
)

# ===========================================================================
# Registry Core Tests
# ===========================================================================


class TestTaskHandlerRegistry:
    """注册表核心测试。"""

    def test_register_and_get(self):
        registry = TaskHandlerRegistry()

        def handler(params):
            return params

        registry.register("send_email", handler)
        assert registry.get("send_email") is handler

    def test_get_unregistered_returns_none(self):
        registry = TaskHandlerRegistry()
        assert registry.get("nonexistent") is None

    def test_has_registered(self):
        registry = TaskHandlerRegistry()
        registry.register("task_a", lambda p: p)
        assert registry.has("task_a")
        assert not registry.has("task_b")

    def test_list_types_empty(self):
        registry = TaskHandlerRegistry()
        assert registry.list_types() == []

    def test_list_types(self):
        registry = TaskHandlerRegistry()
        registry.register("a", lambda p: p)
        registry.register("b", lambda p: p)
        registry.register("c", lambda p: p)

        types = registry.list_types()
        assert set(types) == {"a", "b", "c"}

    def test_overwrite_handler(self):
        registry = TaskHandlerRegistry()

        def handler_v1(params):
            return "v1"

        def handler_v2(params):
            return "v2"

        registry.register("task", handler_v1)
        registry.register("task", handler_v2)
        assert registry.get("task") is handler_v2


# ===========================================================================
# Decorator Tests
# ===========================================================================


class TestHandlerDecorator:
    """装饰器注册测试。"""

    def test_decorator_registers_handler(self):
        registry = TaskHandlerRegistry()

        @registry.handler("send_notification")
        def handle_notification(params):
            return {"sent": True}

        assert registry.has("send_notification")
        assert registry.get("send_notification") is handle_notification

    def test_decorator_with_async_handler(self):
        registry = TaskHandlerRegistry()

        @registry.handler("async_task")
        async def handle_async(params):
            return {"done": True}

        assert registry.has("async_task")
        assert registry.get("async_task") is handle_async

    def test_decorator_preserves_function(self):
        registry = TaskHandlerRegistry()

        @registry.handler("my_task")
        def my_handler(params):
            """My docstring."""
            return params

        assert my_handler.__name__ == "my_handler"
        assert my_handler.__doc__ == "My docstring."

    def test_multiple_decorators(self):
        registry = TaskHandlerRegistry()

        @registry.handler("task_a")
        def handler_a(params):
            return "a"

        @registry.handler("task_b")
        def handler_b(params):
            return "b"

        assert registry.has("task_a")
        assert registry.has("task_b")
        assert len(registry.list_types()) == 2


# ===========================================================================
# Async Detection Tests
# ===========================================================================


class TestAsyncDetection:
    """异步处理器检测测试。"""

    def test_sync_handler_detected(self):
        def sync_fn(params):
            return params

        assert not TaskHandlerRegistry.is_async_handler(sync_fn)

    def test_async_handler_detected(self):
        async def async_fn(params):
            return params

        assert TaskHandlerRegistry.is_async_handler(async_fn)

    def test_lambda_is_sync(self):
        assert not TaskHandlerRegistry.is_async_handler(lambda p: p)

    def test_class_method_sync(self):
        class Handler:
            def process(self, params):
                return params

        h = Handler()
        assert not TaskHandlerRegistry.is_async_handler(h.process)

    def test_class_method_async(self):
        class Handler:
            async def process(self, params):
                return params

        h = Handler()
        assert TaskHandlerRegistry.is_async_handler(h.process)


# ===========================================================================
# Module-level Default Registry Tests
# ===========================================================================


class TestDefaultRegistry:
    """模块级默认注册表测试。"""

    def test_get_default_registry_returns_instance(self):
        registry = get_default_registry()
        assert isinstance(registry, TaskHandlerRegistry)

    def test_get_default_registry_singleton(self):
        r1 = get_default_registry()
        r2 = get_default_registry()
        assert r1 is r2

    def test_task_handler_decorator(self):
        @task_handler("default_registry_test_task")
        def handle_test(params):
            return params

        registry = get_default_registry()
        assert registry.has("default_registry_test_task")
