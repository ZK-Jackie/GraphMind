from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, ConfigDict

default_level_prefix = ["书籍名称", "一级标题", "二级标题", "三级标题", "四级标题", "五级标题", "六级标题", "七级标题",
                        "八级标题", "正文文本"]


class PromptFactory(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    def build_insertion(prompt_template: str,
                        level: int,
                        level_content: str,
                        level_prefix: list[str] = None) -> str:
        """构建插入语句"""
        if level_prefix is None:
            level_prefix = default_level_prefix
        return (PromptTemplate
                .from_template(prompt_template)
                .invoke({"level_name": level_prefix[level], "level_content": level_content})
                .to_string())
