import os

from pydantic import model_validator
from tqdm import tqdm
from logging import getLogger
from chatkg.adapter.engine.base import BaseEngine
from langchain_core.prompts import PromptTemplate
from chatkg.adapter.structure.InfoTree import InfoTreeTask, InfoTreeTaskResult, tree_task_serialize
from chatkg.adapter.task_model.zhipu import TaskZhipuAI
from chatkg.utils.text_reader.MarkdownReader import MarkdownReader
from chatkg.adapter.engine.support_config import TRADITION_SUPPORT


import json
import warnings

default_system_prompt = (
    "你是一个知识提取助手，你的任务是分析用户提供的文本，并从中提取关键信息。"
    "在提取信息时，请专注于事实、数据点和关键概念。"
    "忽略非关键细节和主观意见。"
    "请以要求的格式提供提取出的知识点。"
)

default_prompt_template = (
    "请根据提供的多级标题和文本内容，执行以下知识提取任务：\n"
    "1. 综合多个等级的标题，从标题中提取出一个或多个知识实体，每个知识实体都是一个知识名词。\n"
    "2. 从**文本内容**中找出这些知识实体的属性名及属性，忽略**文本内容**中的例题、分析、答案。\n"
    "3. 从标题之间、标题与正文之间、正文之间找出或总结出提取的实体之间的关系词。\n"
    "4. 将提取的内容以JSON字符串格式输出。\n\n"
    "## 输入内容\n"
    "{insertion}"
    "## 输出格式\n"
    "输出应为一个JSON字符串，包含以下结构：\n"
    "- **知识实体**：从标题中提取出，包含知识实体及其属性。\n"
    "- **实体关系**：从**文本内容**中提取出，描述知识实体之间的关系。\n"
    "## 输出示例\n"
    "```json{output_format}```"
)

default_insertion_template = (
    "**{level_name}**：\n"
    "```markdown\n"
    "{level_content}\n"
    "```\n\n"
)

default_level_names = ["书籍名称", "一级标题", "二级标题", "三级标题", "四级标题", "五级标题", "六级标题", "七级标题",
                       "八级标题"]
default_content_names = "文本内容"

default_output_format = """
    {
      "知识实体": {
        "实体1": {
          "属性1": "...",
          "属性2": "......",
          ...
        },
        "实体2": {
          ...
        }
      },
      "实体关系": {
        "实体1": {
          "关系词1": ["实体2", "实体3"],
          "关系词2": ["实体4"],
          ...
        },
        "实体2": {
          "关系词1": [...],
          ...
        },
      }
    }
"""

logger = getLogger(__name__)

tree_type = ["tree", "info_tree", "Tree", "InfoTree"]
raw_type = ["raw", "Raw", "RAW"]

support_struct_types = tree_type


class TraditionEngine(BaseEngine):
    _final_result: list = []

    _execute_success_cnt: int = 0
    _execute_unprocessed_cnt: int = 0
    _execute_failed_cnt: int = 0

    @model_validator(mode="before")
    def validate_struct_type(cls, values):
        struct_type = values.get("struct_type")
        if not struct_type:
            values["struct_type"] = "default"
            warnings.warn("No structure type provided, using default structure type.")
        elif struct_type not in TRADITION_SUPPORT:
            raise ValueError(
                f"Unsupported structure type: {struct_type}, should be one of {TRADITION_SUPPORT}")
        return values

    def _execute_reader(self, **reader_kwargs):
        # 读取文件，构造 InfoTree
        return self.reader.indexing()

    def _execute_task_maker(self, info):
        # 初始化 task 列表
        tasks = []
        # 遍历 info 树，构造 task
        for info_tree in info:
            for node_title_list, node_content in info_tree:
                if not node_content:
                    continue
                # 1. 准备插入语，准备路径数组
                source_list = []
                temp_insertions = ""
                for i, title in enumerate(node_title_list):
                    temp_insertions += default_insertion_template.format(level_name=default_level_names[i],
                                                                         level_content=title)
                    source_list.append(title)
                temp_insertions += default_insertion_template.format(level_name=default_content_names,
                                                                     level_content=node_content)
                # 2. 准备 prompt
                temp_prompt = (PromptTemplate
                               .from_template(default_prompt_template)
                               .invoke({"insertion": temp_insertions, "output_format": default_output_format})
                               .to_string())

                # 3. 构建 task，填补 prompt 添加到 tasks 列表中
                temp_task_result = InfoTreeTaskResult(source=source_list, entity=[], relation=[])
                temp_task = InfoTreeTask(task_system_prompt=default_system_prompt,
                                         task_user_prompt=temp_prompt,
                                         task_result=temp_task_result,
                                         task_id=None, task_status="UNPROCESS")
                tasks.append(temp_task)
        return tasks

    def execute(self, **kwargs):
        # 0 造工作目录
        os.makedirs(self.work_dir, exist_ok=True)
        # 1 调用 reader
        info = self._execute_reader()
        # 根据每一个 info 节点构造一个 task
        tasks = self._execute_task_maker(info)
        # 2. 调用 TaskLLM，构建知识图谱
        executing_tasks_progress = tqdm(total=info.count_node(), desc="Executing tasks")
        try:
            # 执行任务
            self.llm.execute_task(tasks, progress_bar=executing_tasks_progress)
            # 整理输出
            for task in tasks:
                try:
                    task.task_result.entity = task.task_output["知识实体"],
                    task.task_result.relation = task.task_output["实体关系"]
                    task.task_status = "SUCCESS"
                    self._execute_success_cnt += 1
                except KeyError:
                    warnings.warn(f"Task {task.task_id} failed")
                    task.task_result.others = task.task_result
                    task.task_status = "UNPROCESSED"
                    self._execute_unprocessed_cnt += 1
                    # TODO 修复：嵌套pydantic json序列化问题——对于info，不要pydantic了！！
                    temp_dict = tree_task_serialize(task)
                    json.dump(temp_dict, open(f"{self.work_dir}/unprocessed_{self._execute_unprocessed_cnt}.json",
                                                     "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        except Exception as e:
            dump_dict = []
            for task in tasks:
                dump_dict.append(tree_task_serialize(task))
                json.dump(tree_task_serialize(dump_dict), open(f"{self.work_dir}/urgent_save.json",
                                          "w", encoding="utf-8"), indent=2,
                          ensure_ascii=False)
            warnings.warn(f"Unexpected exception occur: {e} \n Tasks has urgently saved in {self.work_dir}")

        # 3. 最终转化输出
        final_res = []
        for task in tasks:
            final_res.append(task.dump_dict())
            json.dump(final_res, open(f"{self.work_dir}/result.json", "w", encoding="utf-8"), indent=2,
                      ensure_ascii=False)
        if self._execute_unprocessed_cnt > 0:
            warnings.warn(
                f"Unprocessed tasks has saved in {self.work_dir}/unprocessed_x.json, you should check it and load it again "
                f"by GraphBuilder.load_fixed_json()"
            )
        self._final_result = final_res
        executing_tasks_progress.close()
        return self


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    task_llm = TaskZhipuAI(llm_name="glm-4-flash", api_key=os.getenv("ZHIPU_API_KEY"))
    task_reader = MarkdownReader(file="ch1.md", skip_mark="<abd>")
    engine = TraditionEngine(llm=task_llm, reader=task_reader).execute()
    print(f"Process finished, you can check the result in {engine.work_dir}")
