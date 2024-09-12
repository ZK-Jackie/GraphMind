import json
import warnings

from tqdm import tqdm
from typing import List
from typing_extensions import Self

from pydantic import model_validator, Field


import prompt.default as prompt

from graphmind.adapter.database import BaseGraphDatabase, GraphNeo4j
from graphmind.adapter.engine import BaseEngine, TraditionEnginePrompt
from graphmind.adapter.structure import BaseTask, InfoTreeTask, InfoTreeTaskResult
from graphmind.adapter.engine.support_config import TRADITION_STRUCT_SUPPORT

tree_type = ["tree", "info_tree", "Tree", "InfoTree"]
raw_type = ["raw", "Raw", "RAW"]

support_struct_types = tree_type


class TraditionEngine(BaseEngine):
    engine_prompt: TraditionEnginePrompt = Field(description="Tradition engine prompt",
                                                 default=TraditionEnginePrompt())

    _final_result: List[BaseTask] = []

    _execute_success_cnt: int = 0
    _execute_unprocessed_cnt: int = 0
    _execute_failed_cnt: int = 0

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
        # 根据每一个 info 节点构造一个 task
        tasks = self._execute_task_maker(info)
        # 2 调用 TaskLLM，构建知识图谱
        executing_tasks_progress = tqdm(total=info.count_node(), desc="Executing tasks")
        try:
            # 执行 task
            self.llm.execute_task(tasks, progress_bar=executing_tasks_progress)
            # 实体化 task 的输出
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

        # 3 最终转化输出
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
                new_final_result.append(InfoTreeTask.from_dict(item))
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

    def _execute_task_maker(self, info):
        """
        execute 方法的子步骤
        构造 task
        """
        # 初始化 task 列表
        tasks = []
        # 遍历 info 树，构造 task
        for info_tree in info:
            for node_title_list, node_content in info_tree:
                if not node_content:
                    continue
                # 1. 构造请求提示词
                temp_prompt = self.engine_prompt.build_prompt(node_title_list, node_content)

                # 2. 构建 task，填补 prompt， 添加到 tasks 列表中
                temp_task_result = InfoTreeTaskResult(source=node_title_list, entity={}, relation=[], others=None)
                temp_task = InfoTreeTask(task_system_prompt=prompt.default_system_prompt,
                                         task_user_prompt=temp_prompt,
                                         task_result=temp_task_result,
                                         task_id=None, task_status="UNPROCESS")
                tasks.append(temp_task)
        return tasks

    def _execute_task_save(self, tasks):
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
            except KeyError:
                warnings.warn(f"Task {task.task_id} failed")
                task.task_result.others = task.task_output
                task.task_status = "UNPROCESSED"
                self._execute_unprocessed_cnt += 1
                json.dump(task.dump_dict(),
                          open(f"{self.work_dir}/unprocessed_{self._execute_unprocessed_cnt}.json",
                               "w", encoding="utf-8"), indent=2, ensure_ascii=False)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    # 方式1
    # task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"), api_key=os.getenv("ZHIPU_API_KEY"))
    # task_reader = MarkdownReader(file="ch1.md", skip_mark="<abd>")
    # engine = TraditionEngine(llm=task_llm, reader=task_reader).execute()
    # print(f"Process finished, you can check the result in {engine.work_dir}")
    # neo4j_db = GraphNeo4j()
    # engine.persist_db(neo4j_db)

    # 方式2
    neo4j_db = GraphNeo4j()
    neo4j_db.persist_work_dir("work_dir/20240903203841")
