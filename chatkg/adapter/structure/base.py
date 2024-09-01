from abc import ABC, abstractmethod
from typing import Union, Dict, Any
from pydantic import BaseModel, Field


class BaseStructure(BaseModel, ABC):
    @abstractmethod
    def get_index(self):
        pass


class BaseTaskResult(BaseModel, ABC):
    @abstractmethod
    def dump_dict(self):
        pass

    @abstractmethod
    def from_dict(self, values: dict):
        pass

    class Config:
        from_attributes = True


class BaseTask(BaseModel, ABC):
    task_id: Any | str | None = Field(default=None)
    task_system_prompt: Any | str | None = Field(default=None)
    task_user_prompt: Any | str | None = Field(default=None)
    task_output: Any | Dict | str | None = Field(default=None)
    task_result: Union[BaseTaskResult, Any, Dict, str, None] = Field(default=None)
    task_status: Any | str | int | None = Field(default=None)

    @abstractmethod
    def dump_dict(self):
        pass

    @abstractmethod
    def from_dict(self, values: dict):
        pass
