"""
数据库类
"""
from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseGraphDatabase(BaseModel, ABC):

    @abstractmethod
    def search(self, query):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def execute_build(self, states):
        pass

    @abstractmethod
    async def a_execute_build(self, states):
        pass
