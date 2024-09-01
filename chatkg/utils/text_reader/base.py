from abc import ABC, abstractmethod
from typing import Dict

from pydantic import BaseModel, field_validator, model_validator

import os

class BaseReader(BaseModel, ABC):
    file: str | list | None
    file_type: str | list | None = None


    @abstractmethod
    def indexing(self):
        pass

    @abstractmethod
    def get_index(self):
        pass

    @field_validator('file_type')
    def check_file_type(cls, value):
        if not value:
            raise ValueError("You must provide a file type to build a graph.")
        if isinstance(value, str):
            value = [value]
        elif isinstance(value, list):
            for v in value:
                if not isinstance(v, str):
                    raise ValueError(f"Invalid file type: {v}")
        else:
            raise ValueError(f"Invalid file type: {value}")
        return value

    @model_validator(mode="before")
    def validate_read_target(cls, values: Dict):
        file = values.get("file")
        file_type = values.get("file_type")
        # 处理文件路径
        if isinstance(file, str):
            # 两种情况：文件路径或目录路径
            if isfile(file):
                file = [file]
            elif isdir(file):
                file_list = []
                list_files(file, file_list, file_type)
                if file_list:
                    file = file_list
                else:
                    raise FileNotFoundError(f"No file was found in: {file}")
            else:
                raise FileNotFoundError(f"File not found: {file}")
        elif isinstance(file, list):
            for f in file:
                if not os.path.isfile(f):
                    raise FileNotFoundError(f"File not found: {f}")
        else:
            raise ValueError(f"Invalid file param: {file}")
        values["file"] = file
        return values


def isdir(path):
    return os.path.isdir(path)

def isfile(path):
    return os.path.isfile(path)


def list_files(directory, file_list, file_type=None):
    # 遍历指定目录下的所有文件和子目录
    for item in os.listdir(directory):
        # 拼接完整的文件或目录路径
        path = os.path.join(directory, item)
        # 如果是目录，递归调用list_files函数
        if isdir(path):
            list_files(path, file_list)
        # 如果是文件，将路径添加到列表中
        else:
            if not file_type:
                file_list.append(path)
            else:
                if path.split(".")[-1] in file_type:
                    file_list.append(path)