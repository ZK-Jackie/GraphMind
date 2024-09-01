import os
from typing import Any, Dict, Optional, List

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, model_validator
from abc import ABC, abstractmethod

from chatkg.adapter.structure.base import BaseTask

"""
聊天的用 Langchain 的 Chat...，执行任务的用 Task...
"""


class BaseTaskModel(BaseModel, ABC):
    # 模型参数
    llm_name: str = Field(default="glm-4-flash")
    llm_kwargs: Dict[str, Any] = Field(default_factory=dict)
    # api连接参数
    api_key: Optional[str] = Field(default=None)
    api_base: Optional[str] = Field(default=None, alias="base_url")
    # 部分模型可能还有别的参数
    app_id: Optional[str] = Field(default=None)
    app_sk: Optional[str] = Field(default=None)
    app_ak: Optional[str] = Field(default=None)

    @model_validator(mode="before")
    def validate_environment(cls, values: Dict):
        # 检查是否提供了 llm api 参数
        values["llm_name"] = values.get("llm_name") or os.getenv("LLM_NAME")
        values["api_key"] = values.get("api_key") or os.getenv("ZHIPU_API_KEY")
        values["api_base"] = values.get("api_base") or os.getenv("ZHIPU_API_BASE")
        return values

    @abstractmethod
    def execute_task(self,
                     task: BaseTask | List[BaseTask],
                     mode="sync",
                     **kwargs):
        pass