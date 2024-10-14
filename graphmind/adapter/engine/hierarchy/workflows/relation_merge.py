import asyncio
import json
import warnings
from uuid import uuid4

import pandas as pd
from langchain_core.prompts import PromptTemplate

from graphmind.adapter.engine.hierarchy.prompts import relation_merge as MERGE_PROMPT
from graphmind.adapter.engine.hierarchy.reporter import GraphmindReporter
from graphmind.adapter.engine.hierarchy.task_llm.chain import task_ainvoke
from graphmind.adapter.reporter.base import BaseProgressReporter
from graphmind.adapter.structure import BaseTask
from graphmind.adapter.structure.tree import InfoForest, InfoNode
from graphmind.core.base import GraphmindModel
from graphmind.utils.llm_output_parser import try_parse_json_object


def execute_relation_merge(forest: InfoForest,
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
    # 2 创建任务
    asyncio.run(create_relation_merge_task(**task_attr))

    return forest


async def create_relation_merge_task(node_list: list[InfoNode],
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
    # 1 读取缓存中的基础关系信息
    # base_df = pd.read_csv(f"{work_dir}/base_relation.csv")
    base_df = pd.read_csv(
        f"D:/Projects/PycharmProjects/GraphMind/graphmind/adapter/engine/hierarchy/work_dir/20241010150248/base_relation.csv")
    final_df = pd.DataFrame(columns=base_df.columns)
    # 2 按照 (node1, node2) 分类
    grouped_df = base_df.groupby(["start", "end"])
    # 3 创建字典，存储每个类别
    grouped_dfs = {(node1, node2): group for (node1, node2), group in grouped_df}
    # 4 执行、构造合并任务
    exe_rel_merge_reporter = reporter.add_workflow("执行关系合并", len(grouped_dfs))

    async def _create_async_tasks(cat_work_dir: str,
                                  cat_work_report: GraphmindReporter,
                                  node_names: tuple[str, str],
                                  one_chunk_group: pd.DataFrame) -> pd.DataFrame:
        if len(one_chunk_group) == 1:
            cat_work_report.update(1)
            return one_chunk_group
        one_chunk_group.reset_index(drop=True, inplace=True)
        # 来源合并
        merge_source = []
        # 两两实体比较
        i = 0  # 默认以第一行为基准，暂时不考虑同名不同实体的情况
        j = i + 1  # 以第一行为基准，其他行合并入内
        while j < one_chunk_group.shape[0]:
            # 构造插入语句，取 i 为结点 1，取 j 为结点 2
            temp_insertion = [{
                "node1": node_names[0], "node2": node_names[1],
                "description": one_chunk_group.loc[i, "description"],
                "relation": one_chunk_group.loc[i, "relation"],
            }, {
                "node1": node_names[0], "node2": node_names[1],
                "description": one_chunk_group.loc[j, "description"],
                "relation": one_chunk_group.loc[j, "relation"],
            }]
            merge_source.append(json.loads(one_chunk_group.loc[i, "source"]))
            merge_source.append(json.loads(one_chunk_group.loc[j, "source"]))
            # 构造提示词
            temp_prompt = PromptTemplate.from_template(MERGE_PROMPT.user_prompt_template).invoke({
                "output_format": MERGE_PROMPT.user_output_format,
                "output_example": MERGE_PROMPT.user_output_example,
                "insertion": json.dumps(temp_insertion, ensure_ascii=False)
            })
            # 构造任务
            temp_merge_task = BaseTask(task_id=str(uuid4()),
                                       task_system_prompt=MERGE_PROMPT.system_prompt,
                                       task_user_prompt=temp_prompt,
                                       task_description="entity_merge",
                                       task_status="UNPROCESS")
            # 执行任务
            await execute_relation_merge_task(temp_merge_task, cat_work_dir, models)
            # 修改表格信息
            if temp_merge_task.task_status == "SUCCESS":
                one_chunk_group.at[i, "description"] = json.dumps(temp_merge_task.task_result["description"],
                                                                  ensure_ascii=False)
                one_chunk_group.at[i, "relation"] = json.dumps(temp_merge_task.task_result["relation"],
                                                               ensure_ascii=False)
            else:
                warnings.warn(f"Failed to merge entity: {name} when comparing item {i} and {j}")
            j += 1
        # 修改共有信息
        one_chunk_group.at[i, "source"] = json.dumps(merge_source, ensure_ascii=False)
        # 返回合并后的 DataFrame 第一行
        cat_work_report.update(1)
        return one_chunk_group.iloc[0:1]

    # 5 构造合并任务
    merged_dfs_task = []
    for name, chunk_group in grouped_dfs.items():
        task = asyncio.create_task(_create_async_tasks(work_dir, exe_rel_merge_reporter, name, chunk_group))
        merged_dfs_task.append(task)

    # 6 等待任务完成
    merged_dfs = await asyncio.gather(*merged_dfs_task)
    # 7 合并结果
    merge_df_reporter = reporter.add_workflow("合并关系结果", len(merged_dfs))
    for df in merge_df_reporter(merged_dfs):
        final_df = pd.concat([final_df, df])
    # 8 重置索引，保存结果
    merge_dump_reporter = reporter.add_workflow("保存最终关系结果", 1)
    final_df.reset_index(drop=True, inplace=True)
    final_df.to_csv(f"{work_dir}/final_entity.csv", index=False)
    final_df.to_parquet(f"{work_dir}/final_entity.parquet", index=False)
    merge_dump_reporter.update(1)


async def execute_relation_merge_task(task: BaseTask,
                                      work_dir: str,
                                      models: GraphmindModel) -> BaseTask:
    # 4 执行合并任务
    await task_ainvoke(models, task)
    try:
        # 转化
        fixed_output, task.task_result = try_parse_json_object(task.task_output)
        # 合并属性
        merge_attr = {
            "description": task.task_result["description"],
            "relation": task.task_result["relation"]
        }
    except Exception as e:
        # 异常处理
        warnings.warn(f"Failed to parse output: {e}")
        with open(f"{work_dir}/cache/execute_entity_merge_task_failed.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(task.model_dump(), ensure_ascii=False))
        task.task_status = "FAILED"
        return task
    # 保存结果
    task.task_status = "SUCCESS"
    task.task_result = merge_attr
    return task
