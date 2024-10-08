from graphmind.adapter.reporter.base import BaseProgressReporter
from graphmind.adapter.structure.tree import InfoForest
from graphmind.core.base import GraphmindModel


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

