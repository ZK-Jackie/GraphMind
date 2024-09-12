from typing import Any
from langchain_core.prompts import PromptTemplate

import prompt.default as def_prompt

class TraditionEnginePrompt:
    """
    Tradition引擎的提示词，后期开放自定义接口
    """

    system_prompt: str = def_prompt.default_system_prompt
    """系统提示词"""

    entity_point: str = "知识实体"
    relation_point: str = "实体关系"
    """实体、关系识别点"""

    user_prompt_template: str = def_prompt.default_prompt_template
    user_prompt_insertion_template: str = def_prompt.default_insertion_template
    user_prompt_output_example: str = def_prompt.default_output_format
    """用户提示词基本模板、插入段模板、输出示例"""

    insertion_level_names: list[str] = def_prompt.default_level_names
    insertion_content_name: str = def_prompt.default_content_name
    """插入段中的标题标签名字、正文标签名字"""

    def build_prompt(self, node_title_list: list[str], node_content: str) -> str:
        """构建用户提示词"""
        # 构造等级标题
        temp_insertions = ""
        for i, title in enumerate(node_title_list):
            temp_insertions += self._build_level_insertion(self.insertion_level_names[i], title)
        # 构造正文
        temp_insertions += self._build_level_insertion(self.insertion_content_name, node_content)
        # 构建提示词
        temp_prompt = (PromptTemplate
                       .from_template(self.user_prompt_template)
                       .invoke({"insertion": temp_insertions, "output_format": self.user_prompt_output_example})
                       .to_string())
        return temp_prompt

    def _build_level_insertion(self, level_name: str, level_content: str) -> str:
        """构建插入段"""
        return self.user_prompt_insertion_template.format(level_name=level_name, level_content=level_content)

    @staticmethod
    def transform_output(func: callable, use_default: bool=True, **kwargs) -> Any:
        """转换输出"""
        return func(**kwargs)