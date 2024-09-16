from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class BaseStructure(BaseModel, ABC):
    @abstractmethod
    def get_index(self):
        pass


class BaseTaskResult(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """pydantic 配置：允许任意类型"""

    @abstractmethod
    def dump_dict(self):
        pass


class BaseTask(BaseModel):
    task_id: Any | None = Field(description="Task ID", default=None)
    """任务ID"""

    task_system_prompt: Any | None = Field(description="System prompt", default=None)
    """LLM 的系统提示词"""

    task_user_prompt: Any | None = Field(description="User prompt", default=None)
    """用户提示词"""

    task_output: Any | None = Field(description="Raw output from llm", default=None)
    """LLM 的原始输出"""

    task_result: Any | None = Field(description="Task result", default=None)
    """放用户可自定义的结构化输出结果，dump的时候不会提及"""

    task_status: Any | None = Field(description="Task executing status", default=None)
    """任务执行状态"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """pydantic 配置：允许任意类型"""

    def dump_dict(self):
        return {
            "task_id": self.task_id,
            "task_system_prompt": self.task_system_prompt,
            "task_user_prompt": self.task_user_prompt,
            "task_output": self.task_output,
            "task_status": self.task_status
        }
