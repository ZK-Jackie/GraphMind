import os
from typing import List
from typing_extensions import Self

from graphmind.adapter.engine.hierarchy.workflows.entity_merge import execute_entity_merge
from graphmind.adapter.engine.hierarchy.workflows.relation_merge import execute_relation_merge
from graphmind.core.base import GraphmindModel, get_default_llm, get_default_embeddings, get_default_database

from graphmind.adapter.structure.tree import BaseTask
from graphmind.adapter.engine.base import BaseEngine
from graphmind.adapter.engine.hierarchy.reporter import GraphmindReporter
from graphmind.adapter.engine.hierarchy.workflows.entity_extract import execute_entity_task
from graphmind.adapter.engine.hierarchy.workflows.indexing import execute_reader
from graphmind.adapter.engine.hierarchy.workflows.relation_extract import execute_relation_task


class HierarchyEngine(BaseEngine):
    _final_result: List[BaseTask] = []
    """最终结果"""

    def execute(self, **kwargs) -> Self:
        """
        执行知识图谱构建任务
        """
        reporter: GraphmindReporter = GraphmindReporter("GraphMind - Hierarchy Engine")
        # 1 调用 reader，构造结构森林
        forest = execute_reader(work_name=self.work_name,
                                work_dir=self.work_dir,
                                reader=self.reader,
                                reporter=reporter,
                                resume=self.resume)
        task_param = {
            "forest": forest,
            "work_dir": self.work_dir,
            "reporter": reporter,
            "resume": self.resume,
            "models": self.models
        }
        # 2 实体提取
        execute_entity_task(**task_param)
        # 3 关系提取
        execute_relation_task(**task_param)
        # 4 实体去重
        execute_entity_merge(**task_param)
        # 5 关系去重
        # execute_relation_merge(**task_param)
        # 6 持久化
        # self.persist()
        return self

    def persist(self, **kwargs) -> Self:
        return self


if __name__ == '__main__':
    from dotenv import load_dotenv

    from graphmind.adapter.reader.markdown import MarkdownReader

    load_dotenv()

    models = GraphmindModel(llm=get_default_llm(),
                            llm_batch_size=os.getenv("LLM_CONCUR_NUM", 20),
                            task_buffer_size=os.getenv("TASK_BUFFER_SIZE", 32),
                            embeddings=get_default_embeddings(),
                            database=get_default_database(debug=True))
    reader = MarkdownReader(file="input", skip_mark="<abd>", file_title="离散数学")

    engine = HierarchyEngine(models=models, reader=reader, work_name="离散数学")

    engine.execute()
