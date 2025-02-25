import asyncio
import threading

def run_coroutine_threadsafe_task(my_task, *args, **kwargs):
    """在新线程中运行协程任务，保证线程安全，且可以直接嵌入到同步代码中"""
    result = None
    exception = None

    def wrapper():
        nonlocal result, exception
        try:
            # 使用asyncio.run()自动管理事件循环
            result = asyncio.run(my_task(*args, **kwargs))
        except Exception as e:
            exception = e

    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    thread.join()  # 等待线程完成

    if exception is not None:
        raise exception
    return result