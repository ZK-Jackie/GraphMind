import json
import os

from graphmind.adapter.engine.hierarchy.reporter import GraphmindReporter
from graphmind.adapter.reader.base import BaseReader
from graphmind.adapter.structure.tree import InfoForest


def execute_reader(work_name: str,
                   work_dir: str,
                   reader: BaseReader,
                   reporter: GraphmindReporter,
                   resume: bool = False) -> InfoForest:
    """
    Hierarchy execute 的子步骤 1——执行 reader 方法，建立索引。
    这个方法执行前，假定所给定的参数全部合理。
    Args:
        work_name: 工作名称/书籍名称
        work_dir: 工作目录
        reader: 文件读取器对象，继承自 BaseReader，必须自己事先完全设置好相关参数
        reporter: 工作汇报器对象
        resume: 是否继续上次的任务

    Returns:
        InfoForest 对象

    """
    work_reporter = reporter.add_workflow("构建索引", total_items=1)
    if resume:
        # 从缓存中读取索引
        forest_from_cache = get_cache(work_dir)
        work_reporter.update(1)
        return forest_from_cache
    # 读取文件，构造森林
    forest: InfoForest = reader.indexing()
    forest.title = work_name
    # 持久化
    dump_cache(work_dir, forest)
    work_reporter.update(1)
    return forest


def dump_cache(work_dir: str, forest: InfoForest):
    """
    将索引持久化到缓存
    Args:
        work_dir: 工作目录
        forest: InfoForest 对象

    """
    cache_dir = f"{work_dir}/cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
    json_dict = forest.model_dump(mode="json")
    with open(f"{cache_dir}/forest.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(json_dict, ensure_ascii=False, indent=4))


def get_cache(work_dir: str) -> InfoForest:
    """
    从缓存中读取索引
    Args:
        work_dir: 工作目录

    Returns:
        InfoForest 对象

    """
    cache_dir = f"{work_dir}/cache"
    with open(f"{cache_dir}/forest.json", "r", encoding="utf-8") as f:
        forest_dict = json.load(f)
    return InfoForest(**forest_dict)
