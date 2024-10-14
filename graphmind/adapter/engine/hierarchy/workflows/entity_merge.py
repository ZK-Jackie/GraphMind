import asyncio
import json
from uuid import uuid4
import warnings

import pandas as pd
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from graphmind.adapter.engine.base import BaseEntity
from graphmind.adapter.engine.hierarchy.prompts import entity_merge as MERGE_PROMPT
from graphmind.adapter.engine.hierarchy.reporter import GraphmindReporter
from graphmind.adapter.engine.hierarchy.task_llm.chain import task_ainvoke
from graphmind.adapter.reporter.base import BaseProgressReporter
from graphmind.adapter.structure import BaseTask
from graphmind.adapter.structure.tree import InfoForest, InfoNode
from graphmind.core.base import GraphmindModel
from graphmind.utils.llm_output_parser import try_parse_json_object


class MergeEntities(BaseModel):
    types: list[str] | None = Field(description="Entity types", default_factory=list)
    """实体类型"""
    names: list[str] | None = Field(description="Entity names", default_factory=list)
    """实体名称"""
    levels: list[int] | None = Field(description="Entity levels", default_factory=list)
    """实体等级"""
    attributes: list[dict] | None = Field(description="Entity attributes", default_factory=list)
    """实体属性"""
    sources: list[list] | None = Field(description="Entity sources", default_factory=list)
    """实体来源"""
    merge_task: BaseTask | None = Field(description="执行实体合并的任务", default=None)
    """实体合并任务信息"""

    def add_base_entity(self, base_entity: BaseEntity):
        self.types.append(base_entity.type)
        self.names.append(base_entity.name)
        self.levels.append(base_entity.level)
        self.attributes.append(base_entity.attributes)
        self.sources.append(base_entity.source)


def execute_entity_merge(forest: InfoForest,
                         work_dir: str,
                         models: GraphmindModel,
                         reporter: BaseProgressReporter = None,
                         resume: bool = False) -> InfoForest | None:
    """
    execute 步骤 2 —— 任务制造器，构造实体提取任务、执行任务。
    Args:
        forest: InfoForest 对象
        work_dir: 工作目录
        models: GraphmindModel 对象，项目模型实体 & 配置
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        InfoForest 对象或 None

    """
    # 初始化 task 列表
    node_list = []
    # 1 遍历 info 树，延展 node
    for tree in forest.iter():
        for node in tree.iter():
            node_content = node.content
            if not node_content:
                continue
            node_list.append(node)
    task_attr = {
        "node_list": node_list,
        "work_name": forest.title,
        "work_dir": work_dir,
        "models": models,
        "reporter": reporter,
        "resume": resume
    }
    # 创建任务
    try:
        asyncio.run(create_entity_merge_task(**task_attr))
    except Exception as e:
        warnings.warn(f"Unexpected error: {e}, forest has urgently saved.")
        with open(f"{work_dir}/cache/execute_entity_merge_task_failed.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(forest.model_dump(), ensure_ascii=False))
    return forest


async def create_entity_merge_task(node_list: list[InfoNode],
                                   work_dir: str,
                                   models: GraphmindModel,
                                   reporter: GraphmindReporter,
                                   resume: bool, **kwargs) -> None:
    """
    创建实体合并任务
    Args:
        node_list: InfoNode 对象列表
        work_dir: 工作目录
        models: GraphmindModel 对象，项目模型实体 & 配置
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务
        **kwargs: 其他参数

    Returns:
        None

    """
    if resume:
        print(node_list, kwargs)
    # 1 读取缓存中的基础实体信息
    base_df = pd.read_csv(f"{work_dir}/base_entity.csv")
    # base_df = pd.read_csv(
    #     f"D:/Projects/PycharmProjects/GraphMind/graphmind/adapter/engine/hierarchy/work_dir/20241009191046/base_entity.csv")
    final_df = pd.DataFrame(columns=base_df.columns)
    # 2 按名字分类汇总
    grouped_df = base_df.groupby("name")
    # 3 创建一个字典来存储每类 entity 的 DataFrame
    grouped_dfs = {str(entity): group for entity, group in grouped_df}
    # 4 执行、构造合并任务
    work_reporter = reporter.add_workflow("执行实体合并", len(grouped_dfs))
    error_pandas = 0

    async def _create_async_tasks(cat_work_dir: str,
                                  cat_work_report: GraphmindReporter,
                                  one_name: str,
                                  one_chunk_group: pd.DataFrame) -> pd.DataFrame:
        if len(one_chunk_group) == 1:
            cat_work_report.update(1)
            return one_chunk_group
        one_chunk_group.reset_index(drop=True, inplace=True)
        # 来源合并
        merge_source = []
        # 类型和等级取众数
        merge_type = one_chunk_group["type"].mode()[0]
        merge_level = one_chunk_group["level"].mode()[0]
        # 两两实体比较
        i = 0  # 默认以第一行为基准，暂时不考虑同名不同实体的情况
        j = i + 1  # 以第一行为基准，其他行合并入内
        while j < one_chunk_group.shape[0]:
            # 构造插入语句，取 i 为结点 1，取 j 为结点 2
            try:
                temp_insertion = [{
                    "实体名称": one_name,
                    "属性": json.loads(one_chunk_group.loc[i, "attributes"])
                }, {
                    "实体名称": one_name,
                    "属性": json.loads(one_chunk_group.loc[j, "attributes"])
                }]
                merge_source.append(json.loads(one_chunk_group.loc[i, "source"]))
                merge_source.append(json.loads(one_chunk_group.loc[j, "source"]))
                # 构造提示词
                temp_prompt = PromptTemplate.from_template(MERGE_PROMPT.user_prompt_template).invoke({
                    "output_format": MERGE_PROMPT.user_output_format,
                    "output_example": MERGE_PROMPT.user_output_example,
                    "insertion": json.dumps(temp_insertion, ensure_ascii=False, indent=None)
                })
                # 构造任务
                temp_merge_task = BaseTask(task_id=str(uuid4()),
                                           task_system_prompt=MERGE_PROMPT.system_prompt,
                                           task_user_prompt=temp_prompt,
                                           task_description="entity_merge",
                                           task_status="UNPROCESS")
                # 执行任务
                await execute_entity_merge_task(temp_merge_task, work_dir, models)
                # 修改表格信息
                if temp_merge_task.task_status == "SUCCESS":
                    one_chunk_group.at[i, "attributes"] = json.dumps(temp_merge_task.task_result, ensure_ascii=False)
                else:
                    warnings.warn(f"Failed to merge entity: {name} when comparing item {i} and {j}")
                    with open(f"{cat_work_dir}/cache/entity_merge_task_failed.jsonl",
                              "a", encoding="utf-8") as f:
                        f.write(json.dumps(temp_merge_task.model_dump(), ensure_ascii=False))
                        f.write("\n")
                with open(f"{cat_work_dir}/cache/entity_merge_task.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(temp_merge_task.model_dump(), ensure_ascii=False))
                    f.write("\n")
            except Exception as e:
                warnings.warn(f"Failed to merge entity when reading {one_chunk_group} with error: {e}")
                one_chunk_group.to_csv(f"{cat_work_dir}/cache/error_base_entity{error_pandas}.csv",
                                       index=False)

            j += 1
        # 修改共有信息
        one_chunk_group.at[i, "type"] = merge_type
        one_chunk_group.at[i, "level"] = merge_level
        one_chunk_group.at[i, "source"] = json.dumps(merge_source, ensure_ascii=False)
        # 返回合并后的 DataFrame 第一行
        cat_work_report.update(1)
        return one_chunk_group.iloc[0:1]

    # 5 构造合并任务
    merged_dfs_task = []
    for name, chunk_group in grouped_dfs.items():
        task = asyncio.create_task(_create_async_tasks(work_dir, work_reporter, name, chunk_group))
        merged_dfs_task.append(task)

    # 6 等待任务完成
    merged_dfs = await asyncio.gather(*merged_dfs_task)
    # 7 合并结果
    merge_df_reporter = reporter.add_workflow("合并实体结果", len(merged_dfs))
    for df in merge_df_reporter(merged_dfs):
        final_df = pd.concat([final_df, df])
    # 8 重置索引，保存结果
    merge_dump_reporter = reporter.add_workflow("保存最终实体结果", 1)
    final_df.reset_index(drop=True, inplace=True)
    final_df.to_csv(f"{work_dir}/final_entity.csv", index=False)
    final_df.to_parquet(f"{work_dir}/final_entity.parquet", index=False)
    merge_dump_reporter.update(1)


async def execute_entity_merge_task(task: BaseTask,
                                    work_dir: str,
                                    models: GraphmindModel) -> BaseTask:
    try:
        # 执行合并任务
        await task_ainvoke(models, task)
        # 解析结果
        result: dict
        # 转化
        fixed_output, result = try_parse_json_object(task.task_output)
        # 合并属性
        merge_attr = (result.get("属性")
                      or result.get("attributes")
                      or result.get("attribute"))
    except Exception as e:
        # 异常处理
        warnings.warn(f"Failed merge entity: {e}")
        with open(f"{work_dir}/cache/merge_entity_failed.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(task.model_dump(), ensure_ascii=False))
        task.task_status = "FAILED"
        return task
    # 6 保存结果
    task.task_status = "SUCCESS"
    task.task_result = merge_attr
    return task
