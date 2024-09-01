from typing import Dict, Union
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, model_validator

import os
import time

from chatkg.adapter.task_model.base import BaseTaskModel
from chatkg.utils.text_reader.base import BaseReader


class BaseEngine(BaseModel, ABC):
    work_dir: str = Field(default=f"{os.getcwd()}/work_dir/{time.strftime('%Y%m%d%H%M%S')}")
    struct_type: str = Field(default="default")
    llm: Union[BaseTaskModel, dict, None]
    reader: Union[BaseReader, dict, None]
    embeddings: Union[BaseTaskModel, dict, None] = None

    @abstractmethod
    def execute(self):
        pass

