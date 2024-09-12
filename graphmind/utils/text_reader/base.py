from abc import ABC, abstractmethod
from typing import Any
from typing_extensions import Self

from pydantic import BaseModel, Field, field_validator, model_validator

import os


class BaseReader(BaseModel, ABC):
    file: str | list | None = Field(description="File path or directory path")
    """输入文件或输入文件目录"""

    file_type: str | list | None = Field(description="File type", default=None)
    """需要处理的文件类型"""

    struct_type: str | None = Field(description="Structure type", default=None)
    """需要读取分析成的结构类型"""

    @abstractmethod
    def indexing(self, **kwargs):
        """
        读取、处理输入文件，将文件编制成特定的struct_type结构，
        典型地，通常将 Markdown 文件根据标题、段落编制成树状结构
        """
        pass

    @abstractmethod
    def get_index(self, **kwargs):
        """
        获取、输出经过了 indexing 方法编制完成后的结构，
        通常用于测试环节，方便调试查看
        """
        pass

    @field_validator('file_type')
    def prevalidate_file_type(cls, values: Any) -> Any:
        """
        预验证 file_type 字段，确保其为 str 或 list[str] 类型
        :param values:  pydantic values
        :return:  pydantic values
        """
        if not values:
            raise ValueError("You must provide a specific file type to read.")
        if isinstance(values, str):
            values = [values]
        elif isinstance(values, list):
            for v in values:
                if not isinstance(v, str):
                    raise ValueError(f"Invalid value input: `{values}`, only `str` or `list[str]` is allowed.")
        else:
            raise ValueError(f"Invalid value input: `{values}`, only `str` or `list[str]` is allowed.")
        return values

    @model_validator(mode="after")
    def preprocess_file(self) -> Self:
        """
        预处理 file 字段，确保其为文件路径或目录路径，最后将其转换为具体的文件路径列表
        :return: pydantic model
        """
        file = self.file
        file_type = self.file_type
        # 处理文件路径
        if isinstance(file, str):
            # 两种情况：文件路径或目录路径
            if _check_isfile(file):
                file = [file]
            elif _check_isdir(file):
                file_list = []
                _list_files(file, file_list, file_type)
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

        self.file = file
        return self


def _check_isdir(path):
    return os.path.isdir(path)


def _check_isfile(path):
    return os.path.isfile(path)


def _list_files(directory, file_list, file_type=None):
    # 遍历指定目录下的所有文件和子目录
    for item in os.listdir(directory):
        # 拼接完整的文件或目录路径
        path = os.path.join(directory, item)
        # 如果是目录，递归调用list_files函数
        if _check_isdir(path):
            _list_files(path, file_list)
        # 如果是文件，将路径添加到列表中
        else:
            if not file_type:
                file_list.append(path)
            else:
                if path.split(".")[-1] in file_type:
                    file_list.append(path)
