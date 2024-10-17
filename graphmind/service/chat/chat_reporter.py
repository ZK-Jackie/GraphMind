import functools
import logging
from typing import Callable

from graphmind.api.grpc.request.chat_status_request import chat_status_report
from graphmind.core.base import BaseReporter
from graphmind.service.chat.base import ChatStatus, StatusEnum
from graphmind.service.chat.chat_context import get_user_message

logger = logging.getLogger(__name__)


class ChatStatusReporter(BaseReporter):
    _report_func: Callable[[ChatStatus], None] = None

    def __init__(self, report_func: Callable[[ChatStatus], None]):
        self._report_func = report_func

    def report_status(self, status: ChatStatus):
        try:
            # 转换成 gRPC 对象给负责 request 的函数
            self._report_func(status)
        except Exception as e:
            logger.warning(f"Failed to report status: {e}")


chat_status_reporter = ChatStatusReporter(chat_status_report)


def status_report(name: str,
                  before_message: str = None,
                  after_message: str = None,
                  final_report: bool = False):
    """
    聊天状态汇报装饰器工厂，制作装饰器

    Args:
        name: 汇报者执行的业务名称
        before_message: 业务函数开始执行前的提示语句
        after_message: 业务函数结束结束后的提示语句
        final_report: 是否是最后一次汇报
    """
    # 1 构造开始前的提示语句
    before_msg = before_message if before_message else f"{name}执行中..."
    # 2 构造结束语句
    after_msg = after_message if after_message else f"{name}执行完毕"
    # 3 构造结束状态
    after_status = StatusEnum.PROCESSED.value if final_report else StatusEnum.PROCESSING.value

    def decorator(func):
        """
        装饰器，提供汇报功能
        """

        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            now_user_message = get_user_message()
            # 开始汇报
            chat_status_reporter.report_status(
                ChatStatus.from_user_message(now_user_message,
                                             status_id=StatusEnum.PROCESSING.value,
                                             status_message=before_msg)
            )
            result = func(*args,**kwargs)
            # 结束汇报
            chat_status_reporter.report_status(
                ChatStatus.from_user_message(now_user_message,
                                             status_id=after_status,
                                             status_message=after_msg)
            )
            return result

        return wrapper

    return decorator


__all__ = ["chat_status_reporter", "status_report"]
