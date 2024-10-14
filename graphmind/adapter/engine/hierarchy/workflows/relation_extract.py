import json
import os
import warnings
from uuid import uuid4

import pandas as pd
from typing import Type

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from graphmind.core.base import GraphmindModel
from graphmind.adapter.engine.base import BaseRelation
from graphmind.adapter.engine.hierarchy.prompt_manager import PromptFactory
from graphmind.adapter.engine.hierarchy.reporter import GraphmindReporter
from graphmind.adapter.engine.hierarchy.task_llm.chain import task_batch
from graphmind.adapter.structure import BaseTask
from graphmind.adapter.structure.tree import InfoForest, InfoNode
from graphmind.adapter.engine.hierarchy.prompts import relation_extract as RELATION_PROMPT

from graphmind.utils.llm_output_parser import try_parse_json_object

prompts = PromptFactory()


def execute_relation_task(forest: InfoForest,
                          work_dir: str,
                          models: GraphmindModel,
                          reporter: GraphmindReporter = None,
                          resume: bool = False) -> InfoForest | None:
    """
    execute 步骤 3 —— 沿用实体构建结果，先两两连接实体，再逐一总结关系。
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
    # 1 遍历 info 树，展平 node
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
    # 2 创建 & 执行连接实体任务
    _create_connect_task(**task_attr)
    _execute_connect_task(**task_attr)
    # 3 缓存
    _dump_csv(node_list, work_dir, reporter, resume)
    # 4 返回结果
    return forest


def _create_connect_task(node_list: list[InfoNode],
                         work_name: str,
                         work_dir: str,
                         reporter: GraphmindReporter = None,
                         resume: bool = False, **kwargs) -> None:
    """
    创建连接实体
    Args:
        node_list: forest 中的所有节点列表
        work_name: 工作名称/书籍名称
        work_dir: 工作目录
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        None

    """
    if resume:
        print(node_list, kwargs)
    # 1 创建任务
    work_reporter = reporter.add_workflow("创建初步关系提取任务", len(node_list))
    for node in work_reporter(node_list):
        if not node.content:
            continue
        # 构造插入语句——等级标题
        temp_insertions = ""
        temp_insertions += prompts.build_insertion(RELATION_PROMPT.prompt_insertion_template, 0, work_name)
        for i, title in enumerate(node.get_title_path()):
            temp_insertions += prompts.build_insertion(RELATION_PROMPT.prompt_insertion_template, i + 1, title)
        # 构造插入语句——正文
        temp_insertions += prompts.build_insertion(RELATION_PROMPT.prompt_insertion_template, -1, node.content)
        # 构建提示词
        temp_prompt = PromptTemplate.from_template(RELATION_PROMPT.user_prompt_template).invoke({
            "book": work_name,
            "insertion": temp_insertions,
            "entity_list": ", ".join(node.get_entity_names()),
            "output_format": RELATION_PROMPT.prompt_output_format,
            "output_example": RELATION_PROMPT.user_output_example
        }).to_string()
        # 创建任务
        node.relation_task = BaseTask(
            task_id=str(uuid4()),
            task_system_prompt=RELATION_PROMPT.system_prompt,
            task_user_prompt=temp_prompt,
            task_description="entity connection",
            task_status="UNPROCESSED",
        )
    return


def _execute_connect_task(node_list: list[InfoNode],
                          work_name: str,
                          work_dir: str,
                          models: GraphmindModel,
                          reporter: GraphmindReporter = None,
                          resume: bool = False, **kwargs) -> None:
    """
    执行连接实体
    Args:
        node_list: forest 中的所有节点列表
        work_name: 工作名称/书籍名称
        work_dir: 工作目录
        models: GraphmindModel 对象，项目模型实体 & 配置
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        None

    """
    if resume:
        print(node_list, kwargs)
    # 1 准备任务
    batch_task_buf = []
    for node in node_list:
        if not node.relation_task:
            continue
        batch_task_buf.append(node.relation_task)
    # 2 执行任务
    work_reporter = reporter.add_workflow("执行初步关系任务", len(batch_task_buf))
    task_batch(models, batch_task_buf, work_reporter, enable_continue=True, reduce_continue=reduce_continue)
    # 3 转化结果
    work_reporter = reporter.add_workflow("解析初步关系任务结果", len(node_list))
    for node in work_reporter(node_list):
        if not node.relation_task:
            continue
        # 解析结果
        try:
            results: list
            # 清理任务输出
            node.relation_task.task_output = node.relation_task.task_output.replace("任务完成", "")
            # 解析任务输出
            fixed_output, results = try_parse_json_object(node.relation_task.task_output, expect_type="list")
            # 存储结果
            node.relation_task.task_result = results
            # 转化结果
            for result in results:
                node.relation.append(BaseRelation(
                    start=result.get("实体1") or result.get("entity1"),
                    end=result.get("实体2") or result.get("entity2"),
                    relation=result.get("关系") or result.get("relationship"),
                    description=result.get("描述") or result.get("description"),
                    source=node.get_title_path()
                ))
        except Exception as e:
            warnings.warn(f"Failed to parse output: {e}, task_id: {node.relation_task.task_id}")
            node.relation_task.task_status = "FAILED"
            with open(f"{work_dir}/cache/relation_connect_task_failed.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(node.relation_task.model_dump(mode="json"), ensure_ascii=False))
                f.write("\n")
        with open(f"{work_dir}/cache/relation_connect_task.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(node.relation_task.model_dump(mode="json"), ensure_ascii=False))
            f.write("\n")
    return


reduce_failed_cnt = 0
merge_failed_cnt = 0


def reduce_continue(old_output: str | None,
                    new_output: str) -> str | None:
    """
    合并多个模型的输出
    Args:
        old_output: 旧输出
        new_output: 新输出

    Returns:
        合并后的 json 字符串，如为 None 则表示合并失败

    """
    if old_output:
        temp_old = old_output.replace("任务完成", "")
    else:
        temp_old = ""
    temp_new = new_output.replace("任务完成", "")
    try:
        old_output, old_results = try_parse_json_object(temp_old, expect_type="list")
        new_output, new_results = try_parse_json_object(temp_new, expect_type="list")
    except Exception as e:
        warnings.warn(f"Failed to parse output: {e},"
                      f"old_output: {old_output[0:30]}...,"
                      f"new_output: {new_output[0:30]}...")
        global reduce_failed_cnt
        reduce_failed_cnt += 1
        with open(f"failed_output_{reduce_failed_cnt}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "old_output": old_output,
                "new_output": new_output
            }, ensure_ascii=False))
            f.write("\n")
        return old_output
    try:
        # 合并结果
        if isinstance(old_results, list) and isinstance(new_results, list):
            old_results.extend(new_results)
        else:
            return old_output
    except Exception as e:
        warnings.warn(f"Failed to merge output: {e}")
        global merge_failed_cnt
        merge_failed_cnt += 1
        with open(f"failed_output_{merge_failed_cnt}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "old_results": old_results,
                "new_results": new_results
            }, ensure_ascii=False))
            f.write("\n")
        return old_output
    return json.dumps(old_results, ensure_ascii=False)


def _dump_cache(work_dir: str, pydantic_object: BaseModel):
    """
    将索引持久化到缓存
    Args:
        work_dir: 工作目录
        pydantic_object: pydantic 对象

    """
    cache_dir = f"{work_dir}/cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
    json_dict = pydantic_object.model_dump(mode="json")
    with open(f"{cache_dir}/forest.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(json_dict, ensure_ascii=False, indent=4))


def _get_cache(work_dir: str, pydantic_class: Type[BaseModel]) -> BaseModel:
    """
    从缓存中读取索引
    Args:
        work_dir: 工作目录
        pydantic_class: pydantic 对象类

    Returns:
        InfoForest 对象

    """
    cache_dir = f"{work_dir}/cache"
    with open(f"{cache_dir}/forest.jsonl", "r", encoding="utf-8") as f:
        json_dict = json.load(f)
    return pydantic_class(json_dict)


def _dump_csv(node_list: list[InfoNode],
              work_dir: str,
              reporter: GraphmindReporter = None,
              resume: bool = False) -> None:
    """
    导出关系抽取结果
    Args:
        node_list: InfoNode 对象列表
        work_dir: 工作目录
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        None

    """
    # 1 目标列名
    columns = ["start", "end", "relation", "description", "source"]
    # 2 创建 DataFrame
    relation_df = pd.DataFrame(columns=columns)
    # 3 填充 DataFrame
    for node in node_list:
        for relation in node.relation:
            new_row = pd.DataFrame(relation.pd_dump(set(columns)), index=[0])
            relation_df = pd.concat([relation_df, new_row], ignore_index=True, axis=0)
    # 4 导出
    relation_df.to_csv(f"{work_dir}/base_relation.csv", index=False)
    relation_df.to_parquet(f"{work_dir}/base_relation.parquet", index=False)
