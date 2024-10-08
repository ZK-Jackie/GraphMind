from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseProgressReporter(BaseModel, ABC):
    work_name: str | None = None
    """工作名字"""
    completed: int | None = None
    """完成数量"""
    total: int | None = None
    """总数量"""
    description: str | None = None
    """描述信息"""
    _logger = None
    """日志器"""

    def set_logger(self, logger):
        """设置日志器"""
        self._logger = logger
        return self

    def get_report(self) -> dict:
        """获取报文"""
        return {
            "work_name": self.work_name,
            "completed": self.completed,
            "total": self.total,
            "description": self.description
        }