import json
import warnings
from uuid import uuid4

import pandas as pd

from langchain_core.prompts import PromptTemplate

from graphmind.adapter.engine.hierarchy.reporter import GraphmindReporter
from graphmind.core.base import GraphmindModel
from graphmind.adapter.engine.hierarchy.workflows.chain import task_chain
from graphmind.adapter.engine.base import BaseEntity
from graphmind.adapter.engine.hierarchy.prompt_manager import PromptFactory
from graphmind.adapter.structure import BaseTask
from graphmind.adapter.structure.tree import InfoForest, InfoNode

from graphmind.adapter.engine.hierarchy.prompts import entity_extract as LEVEL_PROMPT
from graphmind.adapter.engine.hierarchy.prompts import entity_attribute as ATTRIBUTE_PROMPT
from graphmind.utils.llm_output_parser import try_parse_json_object

prompts = PromptFactory()


def execute_entity_task(forest: InfoForest,
                        work_dir: str,
                        models: GraphmindModel,
                        reporter: GraphmindReporter = None,
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
    # 2 创建 & 执行等级任务
    _create_level_task(**task_attr)
    _execute_level_task(**task_attr)
    # 3 创建 & 执行属性任务
    _create_attribute_task(**task_attr)
    _execute_attribute_task(**task_attr)
    # 4 缓存表格
    _dump_csv(node_list, work_dir, reporter, resume)
    return forest


def _dump_csv(node_list: list[InfoNode],
              work_dir: str,
              reporter: GraphmindReporter = None,
              resume: bool = False) -> None:
    """
    导出实体任务结果
    Args:
        node_list: InfoNode 对象列表
        work_dir: 工作目录
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        None

    """
    # 1 目标列名字
    columns = ["type", "name", "level", "attributes", "source"]
    # 2 创建表格
    entity_df = pd.DataFrame(columns=columns)
    # 3 遍历节点，填充表格
    for node in node_list:
        for entity in node.entity:
            new_row = pd.DataFrame(entity.pd_dump(include=set(columns)), index=[0])
            entity_df = pd.concat([entity_df, new_row], ignore_index=True, axis=0)
    # 4 导出表格
    entity_df.to_csv(f"{work_dir}/base_entity.csv", index=False)


def _create_level_task(node_list: list[InfoNode],
                       work_name: str,
                       work_dir: str,
                       reporter: GraphmindReporter = None,
                       resume: bool = False, **kwargs) -> None:
    """
    execute 方法的子步骤 3 —— 任务制造器，构造实体等级划分任务、执行任务。
    Args:
        node_list: forest 中的所有节点列表
        work_name: 工作名称/书籍名称
        work_dir: 工作目录
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:

    """
    # 1 创建任务
    work_reporter = reporter.add_workflow("创建实体提取任务", len(node_list))
    for node in work_reporter(node_list):
        if not node.content:
            continue
        # 构造插入语句——等级标题
        temp_insertions = ""
        temp_insertions += prompts.build_insertion(LEVEL_PROMPT.prompt_insertion_template, 0, work_name)
        for i, title in enumerate(node.get_title_path()):
            temp_insertions += prompts.build_insertion(LEVEL_PROMPT.prompt_insertion_template, i + 1, title)
        # 构造插入语句——正文
        temp_insertions += prompts.build_insertion(LEVEL_PROMPT.prompt_insertion_template, -1, node.content)
        # 构建提示词
        temp_prompt = PromptTemplate.from_template(LEVEL_PROMPT.user_prompt_template).invoke({
            "book": work_name,
            "insertion": temp_insertions,
            "output_format": LEVEL_PROMPT.prompt_output_format,
            "output_example": LEVEL_PROMPT.user_output_example
        }).to_string()
        # 插入任务
        node.entity_level_task = BaseTask(task_id=str(uuid4()),
                                          task_system_prompt=LEVEL_PROMPT.system_prompt,
                                          task_user_prompt=temp_prompt,
                                          task_description="entity extraction and level division",
                                          task_status="UNPROCESSED")
    return


def _execute_level_task(node_list: list[InfoNode],
                        work_dir: str,
                        models: GraphmindModel,
                        reporter: GraphmindReporter = None,
                        resume: bool = False, **kwargs) -> None:
    """
    execute 方法的子步骤 4 —— 任务制造器，构造实体等级划分任务、执行任务。
    Args:
        node_list: forest 中的所有节点列表
        work_dir: 工作目录
        models: GraphmindModel 对象，项目模型实体 & 配置
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        无

    """
    # 1 任务执行
    work_reporter = reporter.add_workflow("执行实体提取任务", len(node_list))
    batch_task_buf = []
    for node in work_reporter(node_list, increment=0):
        if not node.entity_level_task:
            work_reporter.update(1)
            continue
        batch_task_buf.append(node.entity_level_task)
        if len(batch_task_buf) >= models.llm_batch_size or node == node_list[-1]:
            # 2 执行任务
            temp_list = [{"system_prompt": task.task_system_prompt, "user_prompt": task.task_user_prompt}
                         for task in batch_task_buf]
            temp_outputs = task_chain(models).batch(temp_list)
            for i, task in enumerate(batch_task_buf):
                task.task_output = temp_outputs[i]
                task.task_status = "PROCESSED"
            work_reporter.update(len(batch_task_buf))
            batch_task_buf = []
    # 3 转化结果
    work_reporter = reporter.add_workflow("解析实体提取任务结果", len(node_list))
    for node in work_reporter(node_list):
        if not node.entity_level_task:
            continue
        # 解析结果
        try:
            fixed_output, results = try_parse_json_object(node.entity_level_task.task_output)
            # 存储结果
            node.entity_level_task.task_result = results
            # 转化结果，注意一个节点可能有多个实体
            for result in results:
                node.entity.append(BaseEntity(
                    type=result.get("实体类型") or result.get("类型") or result.get("type"),
                    name=result.get("实体名称") or result.get("名称") or result.get("name"),
                    level=result.get("评级") or result.get("level"),
                    attributes={
                        "评级解释": result.get("评级解释") or result.get("解释") or result.get("explanation")
                    },
                    source=node.get_title_path()
                ))
                node.entity_level_task.task_status = "SUCCESS"
        except Exception as e:
            warnings.warn(f"Failed to parse output: {e}")
            node.entity_level_task.task_status = "FAILED"
            with open(f"{work_dir}/cache/entity_level_task_failed.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(node.entity_level_task.model_dump(), ensure_ascii=False) + "\n")
        # 4 缓存进度
        with open(f"{work_dir}/cache/entity_level_task.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(node.entity_level_task.model_dump(), ensure_ascii=False) + "\n")
    return


def _create_attribute_task(node_list: list[InfoNode],
                           work_name: str,
                           work_dir: str,
                           reporter: GraphmindReporter = None,
                           resume: bool = False, **kwargs) -> None:
    """
    execute 方法的子步骤 5 —— 任务制造器，构造实体属性提取任务、执行任务。
    Args:
        node_list: forest 中的所有节点列表
        work_name: 工作名称
        work_dir: 工作目录
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        无

    """
    # 1 创建任务
    work_reporter = reporter.add_workflow("创建实体属性提取任务", len(node_list))
    for node in work_reporter(node_list):
        if not node.entity:
            continue
        # 构造插入语句——等级标题
        temp_insertions = ""
        temp_insertions += prompts.build_insertion(ATTRIBUTE_PROMPT.prompt_insertion_template, 0, work_name)
        for i, title in enumerate(node.get_title_path()):
            temp_insertions += prompts.build_insertion(ATTRIBUTE_PROMPT.prompt_insertion_template, i, title)
        # 构造插入语句——正文
        temp_insertions += prompts.build_insertion(ATTRIBUTE_PROMPT.prompt_insertion_template, -1, node.content)
        # 构造实体列表
        entity_list = [entity.name for entity in node.entity]
        entity_list_chunks = [entity_list[i:i + 5] for i in range(0, len(entity_list), 5)]
        # 构建提示词
        for chunk in entity_list_chunks:
            temp_prompt = PromptTemplate.from_template(ATTRIBUTE_PROMPT.user_prompt_template).invoke({
                "book": work_name,
                "insertion": temp_insertions,
                "output_format": ATTRIBUTE_PROMPT.prompt_output_format,
                "output_example": ATTRIBUTE_PROMPT.user_output_example,
                "entity_list": chunk
            }).to_string()
            # 插入任务
            node.entity_attr_task.append(BaseTask(task_id=str(uuid4()),
                                                  task_system_prompt=ATTRIBUTE_PROMPT.system_prompt,
                                                  task_user_prompt=temp_prompt,
                                                  task_description="entity attribute extraction",
                                                  task_status="UNPROCESSED"))
    return


def _execute_attribute_task(node_list: list[InfoNode],
                            work_dir: str,
                            models: GraphmindModel,
                            reporter: GraphmindReporter = None,
                            resume: bool = False, **kwargs) -> InfoForest | None:
    """
    execute 方法的子步骤 6 —— 任务制造器，构造实体属性提取任务、执行任务。
    Args:
        node_list: forest 中的所有节点列表
        work_dir: 工作目录
        models: GraphmindModel 对象，项目模型实体 & 配置
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        无
    """
    # 1 任务执行
    work_reporter = reporter.add_workflow("执行实体属性提取任务", __count_entity(node_list))
    batch_task_buf = []
    for node in work_reporter(node_list, increment=0):
        if not node.entity_attr_task:
            work_reporter.update(1)
            continue
        batch_task_buf.extend(node.entity_attr_task)
        if len(batch_task_buf) > models.llm_batch_size or node == node_list[-1]:
            # 2 执行任务
            temp_list = [{"system_prompt": task.task_system_prompt, "user_prompt": task.task_user_prompt}
                         for task in batch_task_buf]
            temp_outputs = task_chain(models).batch(temp_list)
            for i, task in enumerate(batch_task_buf):
                task.task_output = temp_outputs[i]
                task.task_status = "PROCESSED"
            work_reporter.update(len(batch_task_buf))
            batch_task_buf = []
    # 3 转化结果
    work_reporter = reporter.add_workflow("解析实体属性提取任务结果", len(node_list))
    for node in work_reporter(node_list):
        if not node.entity_attr_task:
            continue
        for task in node.entity_attr_task:
            try:
                # 解析结果
                fixed_output, result = try_parse_json_object(task.task_output)
                # 存储结果
                task.task_result = result
                # 转化结果
                for entity in node.entity:
                    if entity.name in result:
                        entity.attributes.update(result.get(entity.name, {}))
                    else:
                        with open(f"{work_dir}/cache/entity_attr_task_failed.jsonl", "a", encoding="utf-8") as f:
                            f.write(json.dumps(task.model_dump(), ensure_ascii=False) + "\n")
                        task.task_status = "FAILED"
                        continue
                task.task_status = "SUCCESS"
            except Exception as e:
                warnings.warn(f"Failed to parse output: {e}")
                task.task_status = "FAILED"
                with open(f"{work_dir}/cache/entity_attr_task_failed.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(task.model_dump(), ensure_ascii=False) + "\n")
            # 4 缓存进度
            with open(f"{work_dir}/cache/entity_attr_task.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(task.model_dump(), ensure_ascii=False) + "\n")
    return


def __count_entity(node_list: list[InfoNode]) -> int:
    """
    计算实体数量
    Args:
        node_list: InfoNode 对象列表

    Returns:
        int

    """
    entity_cnt = 0
    for node in node_list:
        entity_cnt += node.get_entity_num()
    return entity_cnt
