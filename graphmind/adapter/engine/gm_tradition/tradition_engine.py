import json
import os
import warnings

import pandas as pd
from tqdm import tqdm
from typing import List
from typing_extensions import Self

from pydantic import model_validator, ConfigDict

from graphmind.adapter.database import BaseGraphDatabase
from graphmind.adapter.engine.base import BaseEngine, BaseEntity, BaseRelation
from graphmind.adapter.engine.gm_tradition.prompt_manager import PromptFactory
from graphmind.adapter.llm import TaskZhipuAI
from graphmind.adapter.structure.tree import BaseTask, InfoForest, InfoNode, BaseStructure
from graphmind.adapter.engine.support_config import TRADITION_ENGINE_SUPPORT


class TraditionEngine(BaseEngine):
    engine_prompt: PromptFactory = PromptFactory()
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
        elif self.struct_type not in TRADITION_ENGINE_SUPPORT:
            raise ValueError(
                f"Unsupported structure type: {self.struct_type}, should be one of {TRADITION_ENGINE_SUPPORT}")
        return self

    def execute(self, **kwargs):
        """
        执行知识图谱构建任务
        """
        # 1 调用 reader，构造结构森林
        info = self._execute_reader(**kwargs)
        try:
            # 2 步骤1：构造实体提取任务
            entity_tasks = self._execute_entity_task_maker(info)
            # 3 步骤2：执行实体提取任务
            self._execute_entity_task(entity_tasks)
            # 阶段性处理、保存（主要针对node）
            self._execute_stage_save_1(info)
            # 4 步骤3：构造关系提取任务
            relation_tasks = self._execute_relation_task_maker(info)
            # 5 步骤4：执行关系提取任务
            self._execute_relation_task(relation_tasks)
            # 阶段性处理、保存（主要针对relation）
            self._execute_stage_save_2(info)
            # 6 步骤5：整理实体表
            self._execute_final_entity(info)
            # 7 步骤6：整理关系表
            self._execute_final_relation(info)
        except Exception as e:
            info.dump_pickle(f"{self.work_dir}/info.pkl")
            raise RuntimeError(f"Failed to execute task: {e}")
        # 阶段性处理，保存提取结果
        # self.persist_local(**kwargs)

        return self

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
        执行 reader 方法，建立索引
        """
        # 读取文件，构造 InfoTree
        return self.reader.indexing(**reader_kwargs)

    def _execute_entity_task_maker(self, info: InfoForest | BaseStructure) -> List[BaseTask] | InfoForest:
        """
        execute 方法的子步骤
        构造实体提取任务
        """
        # 初始化 task 列表
        entity_tasks = []
        # 遍历 info 树，构造 task
        for info_tree in info:
            for info_node in info_tree:
                node_content = info_node.content
                node_title_list = info_node.get_title_path()
                if not node_content:
                    continue
                # 1. 构造请求提示词
                temp_user_prompt = self.engine_prompt.entity_extract_builder(node_title_list, node_content)
                # 2. 构建 task，填补 prompt， 添加到 tasks 列表中
                temp_task = BaseTask(task_system_prompt=self.engine_prompt.entity_system_prompt,
                                      task_user_prompt=temp_user_prompt,
                                      task_id=None, task_status="UNPROCESS")
                # 3. 添加到节点信息当中
                info_node.entity_task = temp_task
                # 4. 添加到任务列表
                entity_tasks.append(temp_task)
        return entity_tasks

    def _execute_entity_task(self, tasks: List[BaseTask]):
        """
        execute 方法的子步骤
        执行实体提取任务，事故高发地段
        """
        try:
            from prompt.output_parser import entity_extract_parser
            # 执行任务
            if tasks:
                progress_bar = tqdm(total=len(tasks), desc="Extracting entities", unit="block")
                self.llm.execute_task(tasks, mode="async", json_output=True, retry_on_error=True,
                                      output_parser=entity_extract_parser, progress_bar=progress_bar)
                progress_bar.close()
        except Exception as e:
            raise RuntimeError(f"Failed to execute entity task: {e}")

    def _execute_stage_save_1(self, info: InfoForest | BaseStructure):
        """
        execute 方法的子步骤
        阶段性保存
        """
        # 转移实体结果
        for tree in tqdm(info, desc="Moving entity results", unit="doc"):
            for node in tree:
                # 当节点有任务且任务成功时，将任务结果转移至节点实体（虽然没想到什么情况下会没任务，但还是写着先吧）
                if node.entity_task and node.entity_task.task_status == "SUCCESS":
                    node.entity = node.entity_task.task_result
                elif node.entity_task:
                    self._execute_failed_cnt += 1
                    # 将失败案例写到文件中
                    try:
                        with open(f"{self.work_dir}/failed_entity_{self._execute_failed_cnt}.json", "a", encoding="utf-8") as f:
                            f.write(f"{node.entity_task.dump_dict()}\n")
                    except Exception as e:
                        warnings.warn(f"Failed to save failed entity task")
        # TODO 保存树结构，可以考虑使用 pickle 或 shelve 或 JSON

    def _execute_stage_save_2(self, info: InfoForest | BaseStructure):
        """
        execute 方法的子步骤
        阶段性保存
        """
        # 转移实体结果
        for tree in tqdm(info, desc="Moving relation results", unit="doc"):
            for node in tree:
                # 当节点有任务且任务成功时，将任务结果转移至节点实体（要是结点提取失败就会没任务）
                if node.relation_task and node.relation_task.task_status == "SUCCESS":
                    node.relation = node.relation_task.task_result
                elif node.relation_task:
                    self._execute_failed_cnt += 1
                    # 将失败案例写到文件中
                    try:
                        with open(f"{self.work_dir}/failed_relation_{self._execute_failed_cnt}.json", "a", encoding="utf-8") as f:
                            f.write(f"{node.relation_task.dump_dict()}\n")
                    except Exception as e:
                        warnings.warn(f"Failed to save failed entity task")
        # TODO 保存树结构，可以考虑使用 pickle 或 shelve 或 JSON

    def _execute_relation_task_maker(self, info: InfoForest | BaseStructure) -> List[BaseTask] | InfoForest:
        """
        execute 方法的子步骤
        构造关系提取任务
        """
        # 初始化 task 列表
        tasks = []
        # 遍历 info 树，构造 task
        for info_tree in info:
            for info_node in info_tree:
                node_content = info_node.content
                node_names = info_node.get_entity_names()
                if not node_content or not node_names:
                    continue
                # 1. 构造请求提示词
                temp_user_prompt = self.engine_prompt.relation_extract_builder(node_names, node_content)
                # 2. 构建 task，填补 prompt， 添加到 tasks 列表中
                temp_task = BaseTask(task_system_prompt=self.engine_prompt.relation_system_prompt,
                                      task_user_prompt=temp_user_prompt,
                                      task_id=None, task_status="UNPROCESS")
                # 3. 添加到节点信息当中
                info_node.relation_task = temp_task
                # 4. 添加到任务列表
                tasks.append(temp_task)
        return tasks

    def _execute_relation_task(self, tasks: List[BaseTask]):
        """
        execute 方法的子步骤
        执行关系提取任务
        """
        from prompt.output_parser import relation_extract_parser
        # 执行任务
        if tasks:
            progress_bar = tqdm(total=len(tasks), desc="Extracting relations", unit="block")
            self.llm.execute_task(tasks, mode="async", json_output=True,
                                  output_parser=relation_extract_parser, progress_bar=progress_bar)
            progress_bar.close()

    def _execute_final_entity(self, forest: InfoForest | BaseStructure):
        """
        execute 方法的子步骤
        整理实体表（有不干净的东西！debug单步调试和直接运行的去重结果是完完全全不一样的！被坑了整整两天！！）
        """
        # 0 初始化实体表
        unique_df = pd.DataFrame(columns=["entity", "type", "source", "attribute", "uid", "level", "content"])
        entity_df = pd.DataFrame(columns=["entity", "type", "source", "attribute", "uid", "level", "content"])
        # 1 遍历树，转移实体结果
        for tree in forest:
            for node in tree:
                if node.entity_task.task_status == "SUCCESS":
                    # 节点转换、插入实体表
                    temp_df = _base_entity_to_df(node.entity, source=node.get_title_path(),
                                                 content=node.content, level=node.level)
                    entity_df = pd.concat([entity_df, temp_df], axis=0)
        # 2 找到名称相同多个列，依照名字形成多个df对象
        grouped = entity_df.groupby('entity')
        # 创建一个字典来存储每个entity的DataFrame
        entity_dfs = {entity: group for entity, group in grouped}
        # 3 构造二阶段任务
        for entity_name in tqdm(entity_dfs, desc="Merging and saving duplicated entities", unit="item"):
            if entity_dfs[entity_name].shape[0] < 2:
                unique_df = pd.concat([unique_df, entity_dfs[entity_name]], axis=0)
                continue
            temp_entity_df = entity_dfs[entity_name]
            temp_entity_df.reset_index(drop=True, inplace=True)
            # 两个两个比较
            i = 0  # 默认以第一行为基准，暂时不考虑同名不同实体的情况
            j = i + 1  # 以第一行为基准，其他行合并入内
            while j < temp_entity_df.shape[0]:
                # 取 i 为结点1
                node1: dict = temp_entity_df.loc[i, "attribute"]
                node1["name"] = temp_entity_df.loc[i, "entity"]
                # 取 j 为结点 2
                node2: dict = temp_entity_df.loc[j, "attribute"]
                node2["name"] = temp_entity_df.loc[j, "entity"]
                # 让 llm 执行合并
                temp_user_prompt = self.engine_prompt.entity_merge_builder(node1, node2)
                temp_task = BaseTask(task_system_prompt=self.engine_prompt.entity_merge_system_prompt,
                                      task_user_prompt=temp_user_prompt,
                                      task_result=None,
                                      task_id=None, task_status="UNPROCESS")
                from prompt.output_parser import entity_merge_parser
                temp_task = self.llm.execute_task(temp_task, mode="sync", json_output=True,
                                                  output_parser=entity_merge_parser)
                # # 修树，可能没必要吧？！
                # _tree_patch_node(forest, temp_entity_df.loc[i, "source"], temp_entity_df.loc[i, "entity"],
                #                  temp_task.task_result, temp_task.task_result["name"])
                # _tree_patch_node(forest, temp_entity_df.loc[j, "source"], temp_entity_df.loc[j, "entity"],
                #                  temp_task.task_result, temp_task.task_result["name"])
                # 修改表格信息
                if temp_task.task_status == "SUCCESS":
                    temp_entity_df.at[i, "attribute"] = temp_task.task_result
                    # 合并 source，并去重
                    combined_list = list(set(temp_entity_df.loc[i, "source"] + temp_entity_df.loc[j, "source"]))
                    temp_entity_df.at[i, "source"] = combined_list
                    # while 循环到末尾，j 递增
                    j += 1
                else:
                    # 任务失败，保存
                    self._execute_failed_cnt += 1
                    # 将失败案例写到文件中
                    try:
                        with open(f"{self.work_dir}/failed_entity_merge_{self._execute_failed_cnt}.json", "a", encoding="utf-8") as f:
                            f.write(f"{temp_task.dump_dict()}\n")
                    except Exception as e:
                        warnings.warn(f"Failed to save failed entity merge task")
            # 取第一行加入到 unique_df
            unique_df = pd.concat([unique_df, temp_entity_df.iloc[0:1]], axis=0)
        # 4 保存唯一实体表
        unique_df.to_csv(f"{self.work_dir}/final_entity.csv", index=False, encoding="utf-8")

    def _execute_final_relation(self, forest: InfoForest | BaseStructure):
        relation_df = pd.DataFrame(columns=["start", "relation", "target", "attribute", "content"])
        for tree in tqdm(forest, desc="Saving relations", unit="doc"):
            for node in tree:
                if node.relation_task and node.relation_task.task_status == "SUCCESS":
                    # 节点转换、插入实体表
                    temp_df = _base_relation_to_df(node.relation, source=node.get_title_path(), content=node.content)
                    relation_df = pd.concat([relation_df, temp_df], axis=0)
        # 保存关系表，理论上是不需要去重的
        relation_df.to_csv(f"{self.work_dir}/final_relation.csv", index=False, encoding="utf-8")


def _base_entity_to_df(base_entities: list[BaseEntity], **kwargs) -> pd.DataFrame:
    """
    将 BaseEntity 转换为 DataFrame
    """
    entity_df = pd.DataFrame(columns=["entity", "type", "source", "attribute", "uid", "level", "content"])
    for entity in base_entities:
        new_row = pd.DataFrame({
            "entity": [entity.name],
            "type": [entity.type],
            "source": [kwargs.get("source")],
            "attribute": [entity.attributes],
            "level": [kwargs.get("level")],
            "uid": [kwargs.get("uid")],
            "content": [kwargs.get("content")]
        })
        entity_df = pd.concat([entity_df, new_row], axis=0)
    return entity_df

def _base_relation_to_df(base_relations: list[BaseRelation], **kwargs) -> pd.DataFrame:
    """
    将 BaseRelation 转换为 DataFrame
    """
    relation_df = pd.DataFrame(columns=["start", "relation", "target", "attribute", "description", "content"])
    for relation in base_relations:
        new_row = pd.DataFrame({
            "start": [relation.start],
            "relation": [relation.relation],
            "target": [relation.end],
            "attribute": [relation.attributes],
            "description": [relation.description],
            "content": [kwargs.get("content")]
        })
        relation_df = pd.concat([relation_df, new_row], axis=0)
    return relation_df


# TODO 这是属于数据结构的操作，后续应放入 structure 中
def _tree_patch_node(forest: InfoForest,
                     target_source: list,
                     target_name: str,
                     new_attribute: dict):
    """
    对 InfoForest 进行去重
    """
    target_node = _find_node_from_forest(forest, target_source)
    if target_node:
        # 修改属性
        for entity in target_node.entity:
            if entity.name == target_name:
                entity.attributes = new_attribute
                return
    else:
        warnings.warn(f"Unexpected error: cannot find node {target_name} in file structure! This could never happen!")


def _find_node_from_forest(forest: InfoForest, source: list) -> InfoNode | None:
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
    from graphmind.utils.text_reader.markdown import MarkdownReader

    load_dotenv()

    # 方式1
    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"),
                           api_key=os.getenv("ZHIPU_API_KEY"),
                           llm_kwargs={
                             'temperature': 0.1,
                           },
                           json_output=True)
    task_reader = MarkdownReader(file="input", skip_mark="<abd>")
    engine = TraditionEngine(llm=task_llm, reader=task_reader, struct_type="tree").execute()
    print(f"Process finished, you can check the result in {engine.work_dir}")
    # neo4j_db = GraphNeo4j()
    # engine.persist_db(neo4j_db)

    # 方式2
    # neo4j_db = GraphNeo4j()
    # neo4j_db.persist_work_dir("work_dir/20240903203841")
