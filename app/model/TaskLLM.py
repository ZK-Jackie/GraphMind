"""
TaskModel.py
这将是一个抽象类，用于规范如何调用LLM、转化LLM的回答，供GraphEngine使用
"""
from pydantic import BaseModel
from abc import ABC, abstractmethod

class TaskLLM(BaseModel, ABC):
    base_url: str | None = None
    api_key: str | None = None
    model_name: str | None = None
    temperature: float | None = None

    @abstractmethod
    def chat(self, text: str):
        pass

    @abstractmethod
    def task_execute(self, text: str):
        pass
