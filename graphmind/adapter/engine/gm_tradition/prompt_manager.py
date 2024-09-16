from langchain_core.prompts import PromptTemplate
import prompt.entity_extract as ENTITY_PROMPT
import prompt.relation_extract as RELATION_PROMPT
import prompt.entity_relation_merge as MERGE_PROMPT
from graphmind.adapter.engine.base import BaseEntity


class PromptFactory:
    entity_system_prompt: str = ENTITY_PROMPT.system_prompt
    """实体系统提示词"""

    relation_system_prompt: str = ENTITY_PROMPT.system_prompt
    """关系系统提示词"""

    entity_merge_system_prompt: str = MERGE_PROMPT.entity_merge_system_prompt
    """实体合并系统提示词"""

    def entity_extract_builder(self, node_title_list: list[str], node_content: str) -> str:
        """构建用户提示词"""
        # 构造插入语句——等级标题
        temp_insertions = ""
        for i, title in enumerate(node_title_list):
            temp_insertions += self._build_level_insertion(ENTITY_PROMPT.text_level_names[i], title)
        # 构造插入语句——正文
        temp_insertions += self._build_level_insertion(ENTITY_PROMPT.text_content_name, node_content)
        # 构建提示词
        temp_prompt = (PromptTemplate
                       .from_template(ENTITY_PROMPT.user_prompt_template)
                       .invoke({"insertion": temp_insertions,
                                "output_format": ENTITY_PROMPT.prompt_output_format,
                                "output_example": ENTITY_PROMPT.user_output_example})
                       .to_string())
        return temp_prompt

    @staticmethod
    def _build_level_insertion(level_name: str, level_content: str) -> str:
        """构建插入语句"""
        return ENTITY_PROMPT.prompt_insertion_template.format(level_name=level_name, level_content=level_content)

    @staticmethod
    def relation_extract_builder(node_list: list, node_content: str) -> str:
        """构建关系提取提示词"""
        # 构造插入语句
        temp_insertions = (PromptTemplate
                           .from_template(RELATION_PROMPT.prompt_insertion_template)
                           .invoke({"entities": node_list, "content": node_content})
                           .to_string())
        # 构建提示词
        temp_prompt = (PromptTemplate
                       .from_template(RELATION_PROMPT.user_prompt_template)
                       .invoke({"insertion": temp_insertions,
                                "entities": node_list,
                                "output_format": RELATION_PROMPT.prompt_output_format})
                       .to_string())
        return temp_prompt

    @staticmethod
    def entity_merge_builder(node1: dict, node2: dict) -> str:
        """构建实体关系合并提示词"""
        # 构造提示词
        temp_prompt = (PromptTemplate
                       .from_template(MERGE_PROMPT.entity_merge_user_template)
                       .invoke({
                            "name1": node1["name"],
                            "attr1": _dict_to_kv_str(node1),
                            "name2": node2["name"],
                            "attr2": _dict_to_kv_str(node2),
                            "output_format": MERGE_PROMPT.entity_merge_output_format})
                       .to_string())
        return temp_prompt

def _dict_to_kv_str(d: dict) -> str:
    """将字典转换为键值对字符串"""
    temp_str = ""
    for k, v in d.items():
        temp_str += f"{k}: {v}"
        if k != list(d.keys())[-1]:
            temp_str += ", "
    return temp_str