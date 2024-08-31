"""
知识图谱构建器
"""
import os
import re
import json
import warnings
import time
from typing import List

from numpy.ma.extras import unique
from tqdm import tqdm
from langchain_core.prompts import PromptTemplate
from chatkg.utils.text_reader.MarkdownReader import MarkdownReader
from chatkg.adapter.database.GraphNeo4j import GraphNeo4j, CypherNodeState
from chatkg.adapter.structuring.InfoTree import InfoTreeTask, InfoTreeTaskResult
from zhipuai import ZhipuAI

from chatkg.adapter.database import CypherRelationState

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


class GraphBuilder:
    file: str | List[str] | None

    engine: str
    prompt_template: str
    insertion_template: str

    doc_struct: str | None = None

    _allowed_engines = ["graphrag", "tradition", "tradition2"]
    _final_result: list | None = None

    def __init__(self,
                 file: str | List[str] | None = None,
                 engine: str = None,
                 prompt_template: str = default_prompt_template,
                 insertion_template: str = default_insertion_template):
        self.file = file
        self.engine = engine
        self.prompt_template = prompt_template
        self.insertion_template = insertion_template

    @property
    def engine(self) -> str:
        return self._engine

    @engine.setter
    def engine(self, new_val: str):
        if new_val not in self._allowed_engines:
            raise ValueError(f"Value must be one of {self._allowed_engines}")
        self._engine = new_val

    def get_doc_trees(self, **engine_kwargs):
        if self.doc_struct is None:
            self.doc_struct = str(MarkdownReader(file=self.file, **engine_kwargs).indexing())
        return self.doc_struct

    def build(self, **engine_kwargs):
        if self.engine == "graphrag":
            self._graphrag_engine(engine_kwargs)
        elif self.engine == "tradition":
            self._tradition_engine(engine_kwargs)
        elif self.engine == "tradition2":
            self._tradition_engine(engine_kwargs)
        return self

    # TODO 以后要封装到 engine 类里面
    def _tradition_engine(self, kwargs):
        # 0. 建立一个缓存工作目录，后续会用到
        temp_dir = f"temp/{time.strftime('%Y%m%d%H%M%S')}"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        success_cnt = 0
        unprocessed_cnt = 0
        # 1. 读取文档，构造 tasks
        tasks = []
        # 1.1 读取文件
        info = MarkdownReader(file=self.file, **kwargs).indexing()
        # 1.2 根据每一个 info 节点构造一个 task
        executing_tasks_progress = tqdm(total=info.count_node(), desc="Executing tasks")
        for info_tree in info:
            for node_title_list, node_content in info_tree:
                if not node_content:
                    continue
                # 1.2.1 准备插入语，准备路径数组
                source_list = []
                temp_insertions = ""
                for i, title in enumerate(node_title_list):
                    temp_insertions += self.insertion_template.format(level_name=default_level_names[i],
                                                                      level_content=title)
                    source_list.append(title)
                temp_insertions += self.insertion_template.format(level_name=default_content_names,
                                                                  level_content=node_content)
                # 1.2.2 准备 prompt
                temp_prompt = (PromptTemplate
                               .from_template(self.prompt_template)
                               .invoke({"insertion": temp_insertions, "output_format": default_output_format})
                               .to_string())
                # 1.2.3 构建 task，填补 prompt 添加到 tasks 列表中
                temp_task_result = InfoTreeTaskResult(source=source_list, entity=[], relation=[])
                temp_task = InfoTreeTask(task_prompt=temp_prompt, task_result=temp_task_result)
                tasks.append(temp_task)
        # 2. 调用 TaskLLM，构建知识图谱
        try:
            # 2.1 从llm参数中获取client，当前这里是智谱AI，后续再做拓展
            client: ZhipuAI = kwargs.get("llm")
            for task in tasks:
                # 2.2 异步、任务式请求（默认）
                temp_response = client.chat.asyncCompletions.create(
                    model=kwargs.get("model"),
                    messages=[
                        {"role": "system", "content": default_system_prompt},
                        {"role": "user", "content": task.task_prompt},
                    ]
                )
                task.task_id = temp_response.id

            # 3. 等待所有任务完成
            for task in tasks:
                temp_response = None
                temp_task_status = "PROCESSING"
                # 3.1 若任务没有完成，循环等待
                while temp_task_status != "SUCCESS":
                    if temp_task_status == "FAILED":
                        warnings.warn(f"Task {task.task_id} failed!")
                        temp_response = {
                            "choices": [
                                {
                                    "message": {
                                        "content": "Task failed!"
                                    }
                                }
                            ]
                        }
                        break
                    time.sleep(2)
                    temp_response = client.chat.asyncCompletions.retrieve_completion_result(id=task.task_id)
                    temp_task_status = temp_response.task_status
                # 3.2 解析 llm 的回答为 json
                dict_result = self._parse_to_json(temp_response.choices[0].message.content)
                try:
                    task.task_result.entity = dict_result["知识实体"]
                    task.task_result.relation = dict_result["实体关系"]
                    task.task_status = "SUCCESS"
                    success_cnt += 1
                except KeyError:
                    warnings.warn(f"Task {task.task_id} failed")
                    task.task_result.others = dict_result
                    task.task_status = "UNPROCESSED"
                    unprocessed_cnt += 1
                    with open(f"{temp_dir}/unprocessed_{unprocessed_cnt}.json", "w", encoding="utf-8") as f:
                        f.write(task.task_result.others["raw"])
                finally:
                    executing_tasks_progress.update(1)
        except Exception as e:
            dump_dict = []
            for task in tasks:
                dump_dict.append(task.dump_dict())
                json.dump(dump_dict, open(f"{temp_dir}/urgent_save.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
            warnings.warn(f"Unexpected exception occur: {e} \n Tasks has urgently saved in {temp_dir}")

        # 4. 最终转化输出
        final_res = []
        for task in tasks:
            final_res.append(task.dump_dict())
            json.dump(final_res, open(f"{temp_dir}/result.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"Process over! Task result has saved in {temp_dir}/result.json")
        if unprocessed_cnt > 0:
            print(f"Unprocessed tasks has saved in {temp_dir}/unprocessed_x.json, you should check it and load it again "
                  f"by GraphBuilder.load_fixed_json()")
        self._final_result = final_res
        return final_res


    # TODO 以后要封装到 LLM 类里面
    def _parse_to_json(self, raw_str: str) -> dict:
        try:
            # 把 json 字符串转换为字典
            out = json.loads(raw_str)
        except Exception as e1:
            # 若生成markdown代码块字符串，需要从代码块中提取json字符串
            try:
                # 从代码块中提取json字符串
                out = json.loads(raw_str.split("```")[1])
            except Exception as e2:
                try:
                    # 从代码块中提取json字符串
                    out = self._extract_json_code_block(raw_str)
                except Exception as e3:
                    # 若都失败，返回原始字符串
                    out = {
                        "raw": raw_str
                    }
                    warnings.warn(f"Failed to parse to json: {raw_str}")
        return out


    def _extract_json_code_block(self, raw_str: str):
        # Regular expression to match ```json ... ```
        pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
        # Find all matches
        matches = pattern.findall(raw_str)
        return json.loads(matches[0])


    # TODO 以后要封装到 engine 类里面
    def _graphrag_engine(self, kwargs):
        pass

    def load(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            self._final_result = json.load(f)
        new_final_result = []
        for item in self._final_result:
            new_final_result.append(InfoTreeTask.load_dict(item))
        self._final_result = new_final_result
        return self

    def persist(self, **kwargs):
        if self._final_result is None:
            raise ValueError("No result to persist")
        # 1. 获取图数据库客户端
        graph = kwargs.get("graph_client")
        # 2. 去重，节点合并（关系不用合并）  测试方案：单纯的结果合并
        extract_node_dict = {}
        for result in self._final_result:
            for node in result.task_result.entity:
                # 此时的 node 都是 key 为名，value 为属性的字典
                result.task_result.entity[node]["source"] = result.task_result.source
                if node not in extract_node_dict:
                    extract_node_dict[node] = result.task_result.entity[node]
                else:
                    extract_node_dict[node] = merge_dicts(extract_node_dict[node], result.task_result.entity[node])
        # 3. 构建成cypher类
        cypher_nodes = []
        for node_name in extract_node_dict:
            cypher_node = CypherNodeState(
                node_type="知识实体",
                node_attr=extract_node_dict[node_name]
            )
            cypher_node.node_attr["name"] = node_name
            cypher_node.node_attr["来源"] = extract_node_dict[node_name]["source"]
            del cypher_node.node_attr["source"]
            cypher_nodes.append(cypher_node)
        cypher_relations = []
        for result in self._final_result:
            for node1 in result.task_result.relation:
                for relation in result.task_result.relation[node1]:
                    if type(result.task_result.relation[node1][relation]) is list:
                        for node2 in result.task_result.relation[node1][relation]:
                            cypher_relation = CypherRelationState(
                                node1_name=node1,
                                node1_type="知识实体",
                                relation_name=relation,
                                node2_name=node2,
                                node2_type="知识实体",
                            )
                            cypher_relations.append(cypher_relation)
                    else:
                        if type(result.task_result.relation[node1][relation]) is not str:
                            warnings.warn(f"relation should be str, but got {type(result.task_result.relation[node1][relation])}")
                            continue
                        cypher_relation = CypherRelationState(
                            node1_name=node1,
                            node1_type="知识实体",
                            relation_name=relation,
                            node2_name=str(result.task_result.relation[node1][relation]),
                            node2_type="知识实体",
                        )
                        cypher_relations.append(cypher_relation)
        # 3. 直接交给图数据库客户端
        graph.execute_build(cypher_nodes)
        graph.execute_build(cypher_relations)
        return self

def merge_dicts(dict1, dict2, skip_keys=None):
    if skip_keys is None:
        skip_keys = ["name", "uid"]
    merged_dict = {}
    # Add all keys from dict1
    for key in dict1:
        if key in dict2:
            # If key exists in both, concatenate their values
            if key not in skip_keys:
                if type(dict1[key]) is list and type(dict2[key]) is list:
                    merged_dict[key] = dict1[key] + dict2[key]
                    merged_dict[key] = list(unique(merged_dict[key]))
                else:
                    merged_dict[key] = str(dict1[key]) + "\n" + str(dict2[key])
        else:
            # If key exists only in dict1
            merged_dict[key] = dict1[key]
    # Add keys from dict2 that are not in dict1
    for key in dict2:
        if key not in merged_dict:
            merged_dict[key] = dict2[key]
    return merged_dict


if __name__ == "__main__":
    """
    GraphBuilder类将会是用户使用本程序的核心类之一，用户将会通过这个类来构建知识图谱。
    下文在演示怎么用这个类来构建知识图谱。
    这个类还在不断完善开发，后续会将每个组件拆分到其他文件中，以便于维护。
    """
    from dotenv import load_dotenv
    load_dotenv()

    zhipu_client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))
    graph_builder = (GraphBuilder(file="temp/ch1.md",
                                  engine="tradition")
                     .build(skip_mark="<abd>",
                            llm=zhipu_client,
                            model="glm-4-0520")
                     )
    # graph_builder = GraphBuilder(engine="tradition").load("temp/20240830205230/result.json")
    graph = GraphNeo4j()
    graph_builder.persist(graph_client=graph)

