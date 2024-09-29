import functools
import time

from graphmind.service.base import StatusEnum, ProcessStatus
from graphmind.service.reporter import BaseReporter


def status_report(name: str = None,
                  before_message: str = None,
                  after_message: str = None,
                  final_report: bool = False,
                  reporter: BaseReporter = None):
    """
    状态汇报装饰器工厂，制作装饰器

    Args:
        name: 汇报者执行的业务名称
        before_message: 业务函数开始执行前的提示语句
        after_message: 业务函数结束结束后的提示语句
        final_report: 是否是最后一次汇报
        reporter: 汇报者实例
    """
    # 1 构造开始前的提示语句
    before_msg = before_message if before_message else f"{name}执行中..."
    # 2 构造结束语句
    after_msg = after_message if after_message else f"{name}执行完毕"
    # 3 构造结束状态
    after_status = StatusEnum.PROCESSED if final_report else StatusEnum.PROCESSING

    def decorator(func):
        """
        装饰器，提供汇报功能
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 开始汇报
            reporter.report(ProcessStatus(
                status_id=StatusEnum.PROCESSING.value,
                status_message=f"{before_msg}",
                send_time=str(time.time())
            ))
            result = func(*args, **kwargs)
            # 结束汇报
            reporter.report(ProcessStatus(
                status_id=after_status,
                status_message=f"{after_msg}",
                send_time=str(time.time())
            ))
            return result

        return wrapper

    return decorator

__all__ = ["status_report"]