import json

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from typing_extensions import Self
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator, ConfigDict

import os
import time

from graphmind.adapter.database import BaseGraphDatabase
from graphmind.adapter.llm.base import BaseTaskLLM, BaseTextEmbeddings
from graphmind.adapter.reader.base import BaseReader
from graphmind.core.base import GraphmindModel


class BaseEngine(BaseModel, ABC):
    work_name: str = Field(description="Work name", default="GraphMind")
    """工作名字"""

    work_id: str = Field(description="Work Id", default=f"{time.strftime('%Y%m%d%H%M%S')}")
    """工作 ID"""

    work_dir: str = Field(description="Work directory", default=None)
    """工作、缓存路径，在validate_workdir中会初始化"""

    resume: bool = Field(default=False)
    """是否继续上次的任务"""

    reader: BaseReader | None = Field(description="Text reader configuration", default=None)
    """文件读取器"""

    models: GraphmindModel | None = Field(description="GraphMind model configuration")
    """GraphMind 模型配置"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """pydantic 配置：允许任意类型"""

    @model_validator(mode="after")
    def validate_workdir(self) -> Self:
        """验证工作目录"""
        self.work_dir = f"{os.getcwd()}/work_dir/{self.work_id}"
        # 检查工作目录是否存在
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir, exist_ok=True)
        else:
            print("History work directory detected")
            self.resume = True
        return self

    @abstractmethod
    def execute(self, **kwargs):
        pass


class BaseEntity(BaseModel):
    type: str | None = Field(description="Entity type", default=None)
    """实体类型"""

    name: str = Field(description="Entity name")
    """实体名字"""

    level: str | int | None = Field(description="Entity level", default=None)
    """实体等级"""

    attributes: dict = Field(description="Entity attributes")
    """实体属性"""

    source: list | str | None = Field(description="Entity source", default=None)
    """实体来源"""

    def pd_dump(self, include: set[str], exclude_kv: tuple[str, set] = None) -> dict[str, list[str]]:
        ret = {}
        for key in include:
            ret[key] = [json.dumps(getattr(self, key), ensure_ascii=False)]
        return ret


    def get_kv_attributes(self) -> str:
        temp_str = ""
        for k, v in self.attributes.items():
            temp_str += f"{k}: {v}"
            if k != list(self.attributes.keys())[-1]:
                temp_str += ", "
        return temp_str


class BaseRelation(BaseModel):
    start: str | None = Field(description="Start node name", default=None)
    """开始节点名字"""

    end: str | None = Field(description="End node name", default=None)
    """结束节点名字"""

    relation: str | None = Field(description="Relation name", default=None)
    """关系名字"""

    description: str | None = Field(description="Relation description", default=None)
    """关系描述"""

    attributes: dict | None = Field(description="Relation attributes", default=None)
    """关系属性"""

    source: list | str | None = Field(description="Entity source", default=None)
    """关系来源"""

    def pd_dump(self, include: set[str]) -> dict[str, list[str]]:
        ret = {}
        for key in include:
            ret[key] = [json.dumps(getattr(self, key), ensure_ascii=False)]
        return ret
