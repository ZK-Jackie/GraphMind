from typing_extensions import Self
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, model_validator

import os
import time

from graphmind.adapter.database import BaseGraphDatabase
from graphmind.adapter.llm.base import BaseTaskLLM, BaseTextEmbeddings
from graphmind.utils.text_reader.base import BaseReader


class BaseEngine(BaseModel, ABC):

    work_dir: str = Field(default=f"{os.getcwd()}/work_dir/{time.strftime('%Y%m%d%H%M%S')}")
    """工作、缓存路径"""

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
        # 检查工作目录是否存在
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir, exist_ok=True)
        else:
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

