import asyncio
from typing import Callable, Any


def async_run(func: Callable[..., ...]) -> Any:
    """
    异步运行装饰器
    Args:
        func: 异步函数

    Returns:
        None
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 如果事件循环已经在运行，使用 create_task 并等待其完成
        task = loop.create_task(Callable[..., Any])
        return loop.run_until_complete(task)
    else:
        # 否则，使用 asyncio.run()
        return asyncio.run(func)
