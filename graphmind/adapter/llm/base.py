import os
from typing import Any, Dict, List

from pydantic import BaseModel, Field, model_validator
from abc import ABC, abstractmethod

from typing_extensions import Self

from graphmind.adapter.structure.base import BaseTask

"""
聊天的用 Langchain 的 Chat...，执行任务的用 Task...
"""


class BaseTaskLLM(BaseModel, ABC):
    # 模型参数
    llm_name: str = Field(default="glm-4-flash")
    llm_kwargs: Dict[str, Any] = Field(default_factory=dict)
    # api连接参数
    api_key: str | None = Field(default=None)
    api_base: str = Field(alias="base_url", default=None)
    # 部分模型可能还有别的参数
    app_id: str | None = Field(default=None)
    app_sk: str | None = Field(default=None)
    app_ak: str | None = Field(default=None)

    @model_validator(mode="before")
    def validate_environment(cls, values: Dict):
        # 检查是否提供了 llm api 参数
        values["llm_name"] = values.get("llm_name") or os.getenv("LLM_NAME")
        values["api_key"] = values.get("api_key") or os.getenv("ZHIPU_API_KEY")
        values["api_base"] = values.get("api_base") or os.getenv("ZHIPU_API_BASE")
        return values

    @model_validator(mode="after")
    def validate_chat(self) -> Self:
        # TODO LLM 连通性检查
        return self

    @abstractmethod
    def execute_task(self,
                     task: BaseTask | List[BaseTask],
                     mode="sync",
                     **kwargs) -> BaseTask | List[BaseTask]:
        pass


class BaseTextEmbeddings(BaseModel, ABC):
    # 模型参数
    embeddings_name: str = Field(default="bge-large-zh-v1.5")
    embeddings_kwargs: Dict[str, Any] = Field(default_factory=dict)
    # api连接参数
    api_key: str | None = Field(default=None)
    api_base: str = Field(default=None)
    # 部分模型可能还有别的参数
    app_id: str | None = Field(default=None)
    app_sk: str | None = Field(default=None)
    app_ak: str | None = Field(default=None)

    @model_validator(mode="before")
    def validate_environment(cls, values: Dict):
        # 检查是否提供了 llm api 参数
        values["embeddings_name"] = values.get("embeddings_name") or os.getenv("EMBEDDINGS_NAME")
        values["api_key"] = values.get("api_key") or os.getenv("EMBEDDINGS_API_KEY")
        values["api_base"] = values.get("api_base") or os.getenv("EMBEDDINGS_API_BASE")
        return values

    @model_validator(mode="after")
    def validate_chat(self) -> Self:
        # TODO embeddings 连通性检查
        return self

    @abstractmethod
    def execute_embeddings(self, text: str, mode="sync", **kwargs):
        pass
