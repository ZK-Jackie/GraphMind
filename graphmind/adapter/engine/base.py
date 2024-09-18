from typing_extensions import Self
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator

import os
import time

from graphmind.adapter.database import BaseGraphDatabase
from graphmind.adapter.llm.base import BaseTaskLLM, BaseTextEmbeddings
from graphmind.utils.text_reader.base import BaseReader


class BaseEngine(BaseModel, ABC):
    work_id: str = Field(description="Work Id", default=f"{time.strftime('%Y%m%d%H%M%S')}")
    """工作 ID"""

    work_dir: str = Field(description="Work directory", default=None)
    """工作、缓存路径，在validate_workdir中会初始化"""

    resume: bool = Field(default=False)
    """是否继续上次的任务"""

    struct_type: str = Field(default="default")
    """要选择数据处理的结构类型"""

    llm: BaseTaskLLM | dict | None = Field(description="Language model configuration", default=None)
    """任务型 LLM"""

    reader: BaseReader | dict | None = Field(description="Text reader configuration", default=None)
    """文件读取器"""

    embeddings: BaseTextEmbeddings | dict | None = Field(description="Embeddings configuration", default=None)
    """任务型嵌入模型"""

    graph_database: BaseGraphDatabase | dict | None = Field(description="Graph database configuration", default=None)
    """图数据库"""

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

    @abstractmethod
    def persist_local(self, **kwargs):
        pass

    @abstractmethod
    def persist_database(self, **kwargs):
        pass


class BaseEntity(BaseModel):
    type: str | None = Field(description="Entity type", default=None)
    """实体类型"""

    name: str | None = Field(description="Entity name", default=None)
    """实体名字"""

    attributes: dict | None = Field(description="Entity attributes", default=None)
    """实体属性"""

    source: list | str | None = Field(description="Entity source", default=None)
    """实体来源"""

    def dump_dict(self):
        return {
            "type": self.type,
            "name": self.name,
            "attributes": self.attributes,
            "source": self.source
        }

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

    def dump_dict(self):
        return {
            "start": self.start,
            "end": self.end,
            "relation": self.relation,
            "description": self.description,
            "attributes": self.attributes,
            "source": self.source
        }
