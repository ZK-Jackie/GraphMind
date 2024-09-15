import json
import os
import warnings

import pandas as pd
from tqdm import tqdm
from typing import List
from typing_extensions import Self

from pydantic import model_validator, Field, ConfigDict

import prompt.default as prompt

from graphmind.adapter.database import BaseGraphDatabase, GraphNeo4j
from graphmind.adapter.engine import BaseEngine
from graphmind.adapter.engine.graphmind_tradition.custom_config import TraditionEnginePrompt
from graphmind.adapter.llm import TaskZhipuAI
from graphmind.adapter.structure import BaseTask, InfoTreeTask, InfoTreeTaskResult, InfoForest, InfoNode, InfoTree
from graphmind.adapter.engine.support_config import TRADITION_STRUCT_SUPPORT
from graphmind.adapter.structure.simple import SimpleTask, SimpleResult
from graphmind.utils.text_reader import MarkdownReader

tree_type = ["tree", "info_tree", "Tree", "InfoTree"]
raw_type = ["raw", "Raw", "RAW"]

support_struct_types = tree_type


class TraditionEngine(BaseEngine):
    engine_prompt: TraditionEnginePrompt = TraditionEnginePrompt()
    """引擎所需的LLM提示词配置"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """pydantic 配置：允许任意类型"""

    _final_result: List[BaseTask] = []
    """最终结果"""

    _execute_success_cnt: int = 0
    _execute_unprocessed_cnt: int = 0
    _execute_failed_cnt: int = 0
    """执行任务情况统计"""

    @model_validator(mode="after")
    def validate_struct_type(self) -> Self:
        """
        验证欲采用的结构类型是否合法
        """
        if not self.struct_type:
            self.struct_type = "default"
            warnings.warn("No structure type provided, using default structure type.")
        elif self.struct_type not in TRADITION_STRUCT_SUPPORT:
            raise ValueError(
                f"Unsupported structure type: {self.struct_type}, should be one of {TRADITION_STRUCT_SUPPORT}")
        return self

    def execute(self, **kwargs):
        """
        执行知识图谱构建任务
        """
        # 1 调用 reader
        info = self._execute_reader(**kwargs)
        # 根据每一个 info 节点构造一个 task，这些 task 会紧紧跟随 info 节点，被 llm 处理，结果被后文实例化
        tasks = self._execute_task_maker(info)
        # 2 调用 TaskLLM，构建知识图谱
        executing_tasks_progress = tqdm(total=info.count_node(), desc="Executing tasks")
        try:
            # 执行 task
            self.llm.execute_task(tasks, progress_bar=executing_tasks_progress)
            # task 的输出实例
            self._execute_task_save(tasks)
        except Exception as e:
            # 异常处理，紧急保存
            dump_dict = []
            for task in tasks:
                dump_dict.append(task.dump_dict())
                json.dump(dump_dict, open(f"{self.work_dir}/urgent_save.json",
                                          "w", encoding="utf-8"), indent=2,
                          ensure_ascii=False)
            warnings.warn(f"Unexpected exception occur: {e} \n Tasks has urgently saved in {self.work_dir}")
        # 3 总结、去重、重新组织
        self._execute_final_entity(info)    # 可能实体和关系表要分开生成
        self._execute_final_relation(info)
        # TODO 生成的关系太难看了，需要思考优化方案，当前思想：从表中拿出两两一组（要去重），让 llm 写 desc 和关系词
        # 4 TODO 这些操作应该是执行过程中无时无刻都在进行的，是重要的 resume 的依据！
        final_res = []
        for task in tasks:
            final_res.append(task.dump_dict())
            json.dump(final_res, open(f"{self.work_dir}/result.json", "w", encoding="utf-8"), indent=2,
                      ensure_ascii=False)
        if self._execute_unprocessed_cnt > 0:
            warnings.warn(
                f"Unprocessed tasks has saved in {self.work_dir}/unprocessed_x.json, you should check it and load it again "
                f"by `GraphBuilder.load_fixed_json()` method"
            )
        self._final_result = final_res
        executing_tasks_progress.close()
        return self

    def load(self, **kwargs):
        """
        从持久化磁盘中重载数据，
        后续要放到resume里面去
        """
        work_dir = kwargs.get("work_dir")
        # 读取结果
        if not work_dir:
            raise ValueError("No work_dir provided")
        else:
            raw_result = []
            try:
                with open(f"{work_dir}/result.json", "r", encoding="utf-8") as f:
                    try:
                        raw_result = json.load(f)
                    except json.JSONDecodeError:
                        warnings.warn(f"Result file in {work_dir} is not a valid json file!")
            except FileNotFoundError:
                warnings.warn(f"No result file found in {work_dir}!")
            new_final_result = []
            for item in raw_result:
                new_final_result.append(InfoTreeTask(item))
            self._final_result = new_final_result
            self.work_dir = work_dir
            return TraditionEngine()

    def persist_local(self, **kwargs):
        """
        本地持久化结果
        """
        # 保存结果
        json.dump(self._final_result, open(f"{self.work_dir}/result.json", "w", encoding="utf-8"), indent=2,
                  ensure_ascii=False)
        return self

    def persist_database(self, graph_db: BaseGraphDatabase, **kwargs):
        """
        持久化到数据库
        """
        # 保存结果
        graph_db.execute_build(self._final_result)
        return self

    def _execute_reader(self, **reader_kwargs):
        """
        execute 方法的子步骤
        执行 reader
        """
        # 读取文件，构造 InfoTree
        return self.reader.indexing(**reader_kwargs)

    def _execute_task_maker(self, info: InfoForest) -> List[InfoTreeTask] | InfoForest:
        """
        execute 方法的子步骤
        构造 task
        """
        # 初始化 task 列表
        tasks = []
        # 遍历 info 树，构造 task
        for info_tree in info:
            for info_node in info_tree:
                node_content = info_node.content
                node_title_list = info_node.get_title_path()
                if not node_content:
                    continue
                # 1. 构造请求提示词
                temp_user_prompt = self.engine_prompt.build_prompt(node_title_list, node_content)
                # 2. 构建 task，填补 prompt， 添加到 tasks 列表中
                temp_task_result = InfoTreeTaskResult(source=node_title_list, entity={}, relation=[], others=None)
                temp_task = InfoTreeTask(task_system_prompt=prompt.default_system_prompt,
                                         task_user_prompt=temp_user_prompt,
                                         task_result=temp_task_result,
                                         task_id=None, task_status="UNPROCESS")
                # 3. 添加到节点信息当中
                info_node.task = temp_task
                # 4. 添加到任务列表
                tasks.append(temp_task)
        return tasks

    def _execute_task_save(self, tasks: List[InfoTreeTask]):
        """
        execute 方法的子步骤
        结构化 task 的输出
        """
        for task in tasks:
            try:
                task.task_result.entity = task.task_output["知识实体"]
                task.task_result.relation = task.task_output["实体关系"]
                task.task_status = "SUCCESS"
                self._execute_success_cnt += 1
            except KeyError or TypeError:
                warnings.warn(f"Task {task.task_id} failed")
                task.task_result.others = task.task_output
                task.task_status = "UNPROCESSED"
                self._execute_unprocessed_cnt += 1
                json.dump(task.dump_dict(),
                          open(f"{self.work_dir}/unprocessed_{self._execute_unprocessed_cnt}.json",
                               "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    def _execute_final_entity(self, forest: InfoForest):
        # 1. 遍历树，转df表格
        entity_df = pd.DataFrame(columns=["entity", "source", "attribute", "content"])
        for tree in forest:
            for node in tree:
                if node.task.task_status == "SUCCESS":
                    # 节点转换、插入实体表
                    temp_df = _node_to_entity_df(node)
                    entity_df = pd.concat([entity_df, temp_df], axis=0)
        # 2. 找到名称相同多个列，依照名字形成多个df对象
        grouped = entity_df.groupby('entity')
        # 创建一个字典来存储每个entity的DataFrame
        entity_dfs = {entity: group for entity, group in grouped}
        # 3. 构造二阶段任务
        for entity_name in tqdm(entity_dfs, desc="Merging duplicated entities"):
            if entity_dfs[entity_name].shape[0] < 2:
                continue
            temp_entity_df = entity_dfs[entity_name]
            temp_entity_df.reset_index(drop=True, inplace=True)
            # 两个两个比较
            for i in range(temp_entity_df.shape[0]):
                j = i + 1
                temp_entity_df.reset_index(drop=True, inplace=True)
                while j < temp_entity_df.shape[0]:
                    # 取 i 行"attribute列"为 node1
                    node1: dict = temp_entity_df.iloc[i, :]["attribute"]
                    node1["name"] = temp_entity_df.iloc[i, :]["entity"]  # 补充 name 信息入属性
                    source1: list = temp_entity_df.iloc[i, :]["source"]
                    # 取 j 为结点 2
                    node2: dict = temp_entity_df.iloc[j, :]["attribute"]
                    node2["name"] = temp_entity_df.iloc[j, :]["entity"]  # 补充 name 信息入属性
                    source2: list = temp_entity_df.iloc[j, :]["source"]
                    # 让 llm 执行合并
                    temp_user_prompt = self.engine_prompt.build_merge_prompt(node1, node2, source1, source2)
                    temp_task = SimpleTask(task_system_prompt=None,
                                           task_user_prompt=temp_user_prompt,
                                           task_result=SimpleResult(result=None),
                                           task_id=None, task_status="UNPROCESS")
                    temp_task = self.llm.execute_task(temp_task, mode="sync", json_output=True)
                    # 整理输出
                    try:
                        final_name = list(temp_task.task_output.keys())[0]
                        final_attribute = temp_task.task_output[final_name]
                    except KeyError:
                        warnings.warn(
                            f"LLM output error when merging {node1['name']} and {node2['name']}, will be seen as different entities")
                        temp_entity_df.loc[j, "entity"] = f"{entity_name}_{j}"
                        _tree_patch_node(forest, source2, node2["name"], node2, f"{entity_name}_{j}")
                        j += 1
                        continue
                    # 更新第 i 行实体表
                    temp_entity_df.iloc[i, :]["entity"] = final_name
                    temp_entity_df.iloc[i, :]["attribute"] = final_attribute
                    # 合并结束，删除第 j 行
                    try:
                        temp_entity_df.drop(j, axis=0, inplace=True)
                    except KeyError:
                        warnings.warn(f"Unexpected error: cannot drop row {j} in entity table! This could never happen!")
                    # 修改信息
                    _tree_patch_node(forest, source1, node1["name"], final_attribute, node1["name"])
                    _tree_patch_node(forest, source2, node2["name"], final_attribute, node1["name"])
                    # while 循环到末尾，j 递增
                    j += 1
        # 4. 再次合并实体表
        entity_df = pd.DataFrame(columns=["entity", "source", "attribute", "content"])
        entity_df = pd.concat([entity_dfs[entity] for entity in entity_dfs], axis=0)
        # 5. 保存实体表
        entity_df.to_csv(f"{self.work_dir}/final_entity.csv", index=False, encoding="utf-8")

    def _execute_final_entity_v2(self, forest: InfoForest):
        # 1. 遍历树，转df表格
        entity_df = pd.DataFrame(columns=["entity", "source", "attribute", "content"])
        for tree in forest:
            for node in tree:
                if node.task.task_status == "SUCCESS":
                    # 节点转换、插入实体表
                    temp_df = _node_to_entity_df(node)
                    entity_df = pd.concat([entity_df, temp_df], axis=0)
        # 2. 找到名称相同多个列，依照名字形成多个df对象
        grouped = entity_df.groupby('entity')
        # 创建一个字典来存储每个entity的DataFrame
        entity_dfs = {entity: group for entity, group in grouped}
        # 3. 构造二阶段任务
        for entity_name in tqdm(entity_dfs, desc="Merging duplicated entities"):
            if entity_dfs[entity_name].shape[0] < 2:
                continue
            temp_entity_df = entity_dfs[entity_name]
            temp_entity_df.reset_index(drop=True, inplace=True)
            # 两个两个比较
            for i in range(temp_entity_df.shape[0]):
                j = i + 1
                temp_entity_df.reset_index(drop=True, inplace=True)
                while j < temp_entity_df.shape[0]:
                    # 取 i 行"attribute列"为 node1
                    node1: dict = temp_entity_df.iloc[i, :]["attribute"]
                    node1["name"] = temp_entity_df.iloc[i, :]["entity"]  # 补充 name 信息入属性
                    source1: list = temp_entity_df.iloc[i, :]["source"]
                    # 取 j 为结点 2
                    node2: dict = temp_entity_df.iloc[j, :]["attribute"]
                    node2["name"] = temp_entity_df.iloc[j, :]["entity"]  # 补充 name 信息入属性
                    source2: list = temp_entity_df.iloc[j, :]["source"]
                    # 构造对比提示词
                    temp_user_prompt = self.engine_prompt.build_compare_prompt(node1, node2, source1, source2)
                    # 构造任务
                    temp_task = SimpleTask(task_system_prompt=None,
                                           task_user_prompt=temp_user_prompt,
                                           task_result=SimpleResult(result=None),
                                           task_id=None, task_status="UNPROCESS")
                    temp_task = self.llm.execute_task(temp_task, mode="sync", json_output=False)
                    if "不是" not in temp_task.task_output and \
                            "否" not in temp_task.task_output:
                        # 如果判定为为同一实体，让 llm 执行合并
                        temp_user_prompt = self.engine_prompt.build_merge_prompt(node1, node2, source1, source2)
                        temp_task = SimpleTask(task_system_prompt=None,
                                               task_user_prompt=temp_user_prompt,
                                               task_result=SimpleResult(result=None),
                                               task_id=None, task_status="UNPROCESS")
                        temp_task = self.llm.execute_task(temp_task, mode="sync", json_output=True)
                        # 整理输出
                        try:
                            final_name = list(temp_task.task_output.keys())[0]
                            final_attribute = temp_task.task_output[final_name]
                        except KeyError:
                            warnings.warn(
                                f"LLM output error when merging {node1['name']} and {node2['name']}, will be seen as different entities")
                            temp_entity_df.loc[j, "entity"] = f"{entity_name}_{j}"
                            _tree_patch_node(forest, source2, node2["name"], node2, f"{entity_name}_{j}")
                            j += 1
                            continue
                        # 更新第 i 行实体表
                        temp_entity_df.iloc[i, :]["entity"] = final_name
                        temp_entity_df.iloc[i, :]["attribute"] = final_attribute
                        # 合并结束，删除第 j 行
                        try:
                            temp_entity_df.drop(j, axis=0, inplace=True)
                        except KeyError:
                            warnings.warn(f"Unexpected error: cannot drop row {j} in entity table! This could never happen!")
                        # 修改信息
                        _tree_patch_node(forest, source1, node1["name"], final_attribute, node1["name"])
                        _tree_patch_node(forest, source2, node2["name"], final_attribute, node1["name"])
                    else:
                        # 如果判定为不是同一实体，修改名字，使其后接1，2，3...
                        temp_entity_df.loc[j, "entity"] = f"{entity_name}_{j}"
                        _tree_patch_node(forest, source2, node2["name"], node2, f"{entity_name}_{j}")
                    # while 循环到末尾，j 递增
                    j += 1
        # 4. 再次合并实体表
        entity_df = pd.concat([entity_dfs[entity] for entity in entity_dfs], axis=0)
        # 5. 保存实体表
        entity_df.to_csv(f"{self.work_dir}/final_entity.csv", index=False, encoding="utf-8")

    def _execute_final_relation(self, forest: InfoForest):
        relation_df = pd.DataFrame(columns=["start", "relation", "target", "attribute", "content"])
        for tree in forest:
            for node in tree:
                if node.task.task_status == "SUCCESS":
                    # 节点转换、插入实体表
                    temp_df = _node_to_relation_df(node)
                    relation_df = pd.concat([relation_df, temp_df], axis=0)
        # 保存关系表，理论上是不需要去重的
        relation_df.to_csv(f"{self.work_dir}/final_relation.csv", index=False, encoding="utf-8")

def _node_to_entity_df(node: InfoNode) -> pd.DataFrame:
    """
    将 InfoNode 转换为实体表
    """
    node_df = pd.DataFrame(columns=["entity", "source", "attribute", "content"])
    for entity_name in node.task.task_result.entity:
        new_row = pd.DataFrame({
            "entity": [entity_name],
            "source": [node.task.task_result.source],
            "attribute": [node.task.task_result.entity[entity_name]],
            "content": [node.content]
        })
        node_df = pd.concat([node_df, new_row], axis=0)

    return node_df

def _node_to_relation_df(node: InfoNode) -> pd.DataFrame:
    """
    将 InfoNode 转换为关系表
    """
    relation_df = pd.DataFrame(columns=["start", "relation", "target", "attribute", "content"])
    for start_name, value in node.task.task_result.relation.items():
        for relationship_name in value:
            if isinstance(value[relationship_name], str):
                new_row = pd.DataFrame({
                    "start": [start_name],
                    "relation": [relationship_name],
                    "target": [value[relationship_name]],
                    "attribute": [{}],
                    "content": [node.content]
                })
                relation_df = pd.concat([relation_df, new_row], axis=0)
            elif isinstance(value[relationship_name], list):
                for target_name in value[relationship_name]:
                    new_row = pd.DataFrame({
                        "start": [start_name],
                        "relation": [relationship_name],
                        "target": [target_name],
                        "attribute": [{}],
                        "content": [node.content]
                    })
                    relation_df = pd.concat([relation_df, new_row], axis=0)
            else:
                warnings.warn(f"Unexpected relation type: {type(value[target_name])}")
    return relation_df

# TODO 这是属于数据结构的操作，后续应放入 structure 中
def _tree_patch_node(forest: InfoForest,
                     target_source: list,
                     target_name: str,
                     new_attribute: dict,
                     new_name: str):
    """
    对 InfoForest 进行去重
    """
    target_node = _find_node_from_forest(forest, target_source)
    if target_node:
        # 找到对应的节点，替换节点信息（其实可能是不必要的）
        target_node.task.task_result.entity[target_name] = new_name
        target_node.task.task_result.entity[new_name] = new_attribute
        # 替换关系内容
        relation_str = json.dumps(target_node.task.task_result.relation, ensure_ascii=False)
        relation_str = relation_str.replace(target_name, new_name)
        target_node.task.task_result.relation = json.loads(relation_str)
    else:
        warnings.warn(f"Unexpected error: cannot find node {target_name} in file structure! This could never happen!")


def _find_node_from_forest(forest: InfoForest, source: list):
    """
    从 InfoForest 中找到节点
    """
    for tree in forest:
        if tree.main_root.title == source[0]:
            return _find_node_from_tree(tree.main_root, source, 0)
    return None

def _find_node_from_tree(now_node: InfoNode, source: list, now_depth: int):
    """
    从 InfoTree 中找到节点
    """
    if now_depth > len(source) - 1:
        return None
    if now_node.title == source[now_depth]:
        if now_depth == len(source) - 1:
            return now_node
        for child in now_node.children:
            temp_node = _find_node_from_tree(child, source, now_depth + 1)
            if temp_node:
                return temp_node
    return None


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()

    # 方式1
    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"), api_key=os.getenv("ZHIPU_API_KEY"), json_output=True)
    task_reader = MarkdownReader(file="ch1.md", skip_mark="<abd>")
    engine = TraditionEngine(llm=task_llm, reader=task_reader, struct_type="tree").execute()
    print(f"Process finished, you can check the result in {engine.work_dir}")
    # neo4j_db = GraphNeo4j()
    # engine.persist_db(neo4j_db)

    # 方式2
    # neo4j_db = GraphNeo4j()
    # neo4j_db.persist_work_dir("work_dir/20240903203841")
