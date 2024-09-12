from abc import ABC, abstractmethod
from typing import Union, Dict, Any
from pydantic import BaseModel


class BaseStructure(BaseModel, ABC):
    @abstractmethod
    def get_index(self):
        pass


class BaseTaskResult(ABC):

    @abstractmethod
    def __init__(self, **data):
        pass

    @abstractmethod
    def dump_dict(self):
        pass

    @staticmethod
    @abstractmethod
    def from_dict(values: dict):
        pass


class BaseTask(ABC):
    task_id: Any | str | None
    task_system_prompt: Any | str | None
    task_user_prompt: Any | str | None
    task_output: Any | Dict | str | None
    task_result: Union[BaseTaskResult, Any, Dict, str, None]
    task_status: Any | str | int | None

    @abstractmethod
    def __init__(self, **data):
        pass

    @abstractmethod
    def dump_dict(self):
        pass

    @staticmethod
    @abstractmethod
    def from_dict(values: dict):
        pass
