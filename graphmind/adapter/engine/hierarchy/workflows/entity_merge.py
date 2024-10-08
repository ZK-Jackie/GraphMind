import asyncio
import json
from uuid import uuid4

import pandas as pd
from anyio import Semaphore
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from unstructured.ingest.v2.example import work_dir
from yaml import warnings

from graphmind.adapter.engine.base import BaseEntity
from graphmind.adapter.engine.hierarchy.prompts import entity_merge as MERGE_PROMPT
from graphmind.adapter.engine.hierarchy.reporter import GraphmindReporter
from graphmind.adapter.engine.hierarchy.workflows.chain import task_batch, task_chain
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
    asyncio.run(create_entity_merge_task(**task_attr))

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
    # 1 读取缓存中的基础实体信息
    base_df = pd.read_csv(
        f"D:/Projects/PycharmProjects/GraphMind/graphmind/adapter/engine/hierarchy/work_dir/20241008133849/base_entity.csv")
    final_df = pd.DataFrame(columns=base_df.columns)
    # 2 按名字分类汇总
    grouped_df = base_df.groupby("name")
    # 创建一个字典来存储每类 entity 的 DataFrame
    grouped_dfs = {str(entity): group for entity, group in grouped_df}
    # 异步任务列表
    async_tasks = []
    # 3 构造合并任务
    work_reporter = reporter.add_workflow("构造合并任务", len(grouped_dfs))
    for name, chunk_group in work_reporter(grouped_dfs.items()):
        if len(chunk_group) == 1:
            final_df = pd.concat([final_df, chunk_group], ignore_index=True)
            continue
        # 来源合并
        merge_source = []
        # 类型和等级取众数
        merge_type = chunk_group["type"].mode()[0]
        merge_level = chunk_group["level"].mode()[0]
        # 构造插入语句
        temp_insertion = []
        for index, row in chunk_group.iterrows():
            # 构造提示词
            temp_insertion.append(
                {
                    "实体名称": name,
                    "属性": json.loads(row["attributes"])
                }
            )
            # 合并来源
            merge_source.append(json.loads(row["source"]))

        # 构造提示词
        temp_prompt = PromptTemplate.from_template(MERGE_PROMPT.user_prompt_template).invoke({
            "output_format": MERGE_PROMPT.user_output_format,
            "output_example": MERGE_PROMPT.user_output_example,
            "insertion": json.dumps(temp_insertion, ensure_ascii=False, indent=None)
        })
        # 构造任务
        task = BaseTask(task_id=str(uuid4()),
                        task_system_prompt=MERGE_PROMPT.system_prompt,
                        task_user_prompt=temp_prompt,
                        task_description="entity_merge",
                        task_status="UNPROCESS")
        # 4 执行合并任务
        async_tasks.append(asyncio.create_task(
            execute_entity_merge_task(task, work_dir, name, merge_type, merge_level, merge_source, models)
        ))
    # 5 执行任务
    final_df = pd.concat([final_df, pd.concat(await asyncio.gather(*async_tasks), ignore_index=True)],
                         ignore_index=True)
    # 6 保存结果
    final_df.to_csv(f"{work_dir}/final_entity.csv", index=False)


async def execute_entity_merge_task(task: BaseTask,
                                    work_dir: str,
                                    name: str,
                                    merge_type: str,
                                    merge_level: int,
                                    merge_source: list,
                                    models: GraphmindModel) -> pd.DataFrame:
    # TODO 进度监控
    async with Semaphore(models.llm_batch_size):
        # 4 执行合并任务
        task.task_output = task_chain(models).invoke({
            "system_prompt": task.task_system_prompt,
            "user_prompt": task.task_user_prompt
        })
        try:
            # 转化
            fixed_output, task.task_result = try_parse_json_object(task.task_output)
            # 合并属性
            merge_attr = task.task_result.get("属性") or task.task_result.get("attributes")
        except Exception as e:
            # 异常处理
            warnings(f"Failed to parse output: {e}")
            with open(f"{work_dir}/cache/execute_entity_merge_task_failed.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(task.model_dump(), ensure_ascii=False))
            return pd.DataFrame()
        # 构造新行
        new_row = pd.DataFrame({
            "type": merge_type,
            "name": name,
            "level": merge_level,
            "attributes": json.dumps(merge_attr, ensure_ascii=False, indent=None),
            "source": json.dumps(merge_source, ensure_ascii=False, indent=None)
        }, index=[0])
        return new_row
