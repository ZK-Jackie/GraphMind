from abc import ABC
from typing import Any


class BaseReporter(ABC):
    """
    项目汇报器基类
    """

    def report_progress(self, progress: Any):
        """汇报工作进度"""
        pass

    def report_status(self, status: Any):
        """汇报执行状态"""
        pass
