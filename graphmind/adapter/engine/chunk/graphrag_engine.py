import asyncio
import os
import time
from pathlib import Path
from typing_extensions import Self
import jinja2
import shutil

import pandas as pd
from neo4j import GraphDatabase

from graphmind.adapter.database import GraphNeo4j
from graphmind.adapter.engine.chunk.persist_neo4j import GraphragPersist
from graphmind.adapter.engine.chunk.graphrag_reporter import GraphragReporter
from graphrag.config import load_config, GraphRagConfig
from graphrag.index.api import build_index

from pydantic import model_validator, Field, ConfigDict

from graphmind.adapter.engine import BaseEngine, SUPPORT_CONFIG
from graphmind.adapter.llm import TaskZhipuAI, EmbeddingsZhipuAI
from graphmind.utils.file_reader import find_file
from graphrag.index.progress.rich import RichProgressReporter


# TODO 从输入输出上看，更加符合一个Builder的机制，后续要修改为Builder类
class GraphragEngine(BaseEngine):
    input_dir: str | list[str] = Field(description="Input file directory")
    """用户文件输入目录"""

    input_type: str | list[str] = Field(description="Input file type", default="txt")
    """用户文件输入类型"""

    run_id: str | None = Field(description="Run ID", default=None)

    entity_types: list[str] = Field(description="Entity types",
                                    default=["概念", "定理", "性质", "原理", "算法", "数学家"])
    """实体类型"""

    skip_workflows: str | list[str] = Field(description="Skip workflows", default=[
        "create_base_documents",
        "create_base_text_units",
        "create_final_communities",
        "create_final_community_reports",
        "create_final_covariates",
        "create_final_documents",
        "create_final_text_units",
        "join_text_units_to_covariate_ids",
        "join_text_units_to_entity_ids",
        "join_text_units_to_relationship_ids"
    ])
    """跳过的工作流配置"""

    config_template_path: str | None = Field(description="Custom configuration file path",
                                             default=f"{os.path.dirname(os.path.abspath(__file__))}/config/template.yaml")
    """自定义配置文件路径"""

    prompt_path: str | None = Field(description="Default configuration file path",
                                    default=f"{os.path.dirname(os.path.abspath(__file__))}/prompts/textbook_zh")
    """默认提示词文件路径"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """pydantic 配置：允许任意类型"""

    @model_validator(mode="after")  # 由于是after模式，字段已经初始化，此处就可以使用self了
    def validate_environment(self) -> Self:
        # 1 检测是否提供了 llm 和 embeddings
        if not self.llm or not self.embeddings:
            raise ValueError("Please provide the llm and embeddings.")
        # 2 检测是否提供了 work_dir
        self.work_dir = self.work_dir or f"{os.getcwd()}/work_dir/{time.strftime('%Y%m%d%H%M%S')}"
        # 3 检测是否提供了 input_dir
        self.input_dir = self.input_dir or os.getenv("INPUT_DIR")
        if not self.input_dir:
            raise ValueError("Please provide the input directory.")
        # 4 检测文件输入类型是否合法
        if isinstance(self.input_type, str):
            self.input_type = [self.input_type]
        if not all([t in SUPPORT_CONFIG.CHUNK_FILE_SUPPORT for t in self.input_type]):
            raise ValueError(f"Unsupported input type: {self.input_type}")
        return self  # 一定不要忘记返回self！！

    # 运行+插入数据库，结束
    def execute(self, **kwargs):
        # 1 初始化工作目录
        self._execute_input_init()
        # 2 初始化配置模板
        self._execute_config_init()
        # 3 从main入口运行Graphrag
        self._execute_graphrag_run()
        # 4 TODO parquet转csv（如果用户在参数中要求）
        # self._execute_output_convert()
        # 5 持久化
        self.persist()
        return self

    def persist(self):
        client = GraphDatabase.driver(self.graph_database.uri,
                                      auth=(self.graph_database.username, self.graph_database.password))
        GraphragPersist(book_name=self.work_name,
                        client=client,
                        folder_path=f"{self.work_dir}/output/{self.run_id}/artifacts").persist()

    def _execute_input_init(self) -> None:
        # 1 找用户目录下的文件，复制文件到input目录
        os.makedirs(f"{self.work_dir}/input", exist_ok=True)
        file_list = find_file(self.input_dir, self.input_type)
        if not file_list:
            raise FileNotFoundError(f"No files found in {self.input_dir}")
        for file in file_list:
            shutil.copy(file, f"{self.work_dir}/input")
        # 2 复制配置模板到工作目录
        shutil.copy(self.config_template_path, f"{self.work_dir}/settings.yaml")
        # 3 复制所有提示词到prompts目录
        shutil.copytree(self.prompt_path, f"{self.work_dir}/prompts")

    def _execute_config_init(self) -> None:
        # 1 读取配置模板
        with open(f"{self.work_dir}/settings.yaml", "r", encoding='utf-8') as f:
            template = f.read()
        # 2 渲染配置模板
        # 先准备好正则表达式
        reg_type_content = "|".join(self.input_type)
        # 填充模板
        template = jinja2.Template(template)
        config = template.render(
            skip_workflows=self.skip_workflows,
            llm_model_name=self.llm.llm_name,
            llm_api_key=self.llm.api_key,
            llm_api_base=self.llm.api_base,
            llm_concur_num=5,

            embeddings_model_name=self.embeddings.embeddings_name,
            embeddings_api_key=self.embeddings.api_key,
            embeddings_api_base=self.embeddings.api_base,
            embeddings_concur_num=1,

            input_file_pattern=f'".*\\\\.({reg_type_content})$"',

            entity_types=self.entity_types,
        )
        # 3 写入配置文件
        with open(f"{self.work_dir}/settings.yaml", "w", encoding='utf-8') as f:
            f.write(config)

    def _execute_graphrag_run(self) -> None:
        # 1 准备启动参数
        self.run_id = time.strftime("%Y%m%d-%H%M%S")
        root = Path(self.work_dir).resolve()
        config = load_config(root, None, self.run_id)
        progress_reporter = GraphragReporter("GraphRAG")
        # 2 从 api 入口启动 GraphRAG
        outputs = asyncio.run(self._graphrag_listened_run(config, self.run_id, progress_reporter))
        # 3 检查是否有错误
        encountered_errors = any(
            output.errors and len(output.errors) > 0 for output in outputs
        )
        progress_reporter.stop()
        if encountered_errors:
            raise RuntimeError("Errors occurred during the pipeline run, see logs for more details.")
        else:
            print("All workflows completed successfully.")

    @staticmethod
    async def _listen_progress_and_report(progress_reporter: RichProgressReporter,
                                          interval=1.0):
        while True:
            if hasattr(progress_reporter, '_progressbar') and progress_reporter._progressbar:
                now_task_name = progress_reporter._progressbar.tasks[-1].description
                time_remaining = progress_reporter._progressbar.tasks[-1].time_remaining
                total_work = progress_reporter._progressbar.tasks[-1].total
                remaining_work = progress_reporter._progressbar.tasks[-1].remaining
                percentage = progress_reporter._progressbar.tasks[-1].percentage
                # 传递进度信息
                print({
                    "now_task_name": now_task_name,
                    "time_remaining": time_remaining,
                    "total_work": total_work,
                    "remaining_work": remaining_work,
                    "percentage": percentage
                })
            # 等待指定的时间间隔
            await asyncio.sleep(interval)

    @staticmethod
    async def _graphrag_listened_run(config: GraphRagConfig,
                                     run_id: str,
                                     progress_reporter: GraphragReporter):
        # 启动 GraphRAG 和
        outputs = await asyncio.gather(
            build_index(
                config=config,
                run_id=run_id,
                is_resume_run=False,
                is_update_run=False,
                memory_profile=False,
                progress_reporter=progress_reporter,
                emit=["parquet"],
            )
        )
        # 返回输出
        return outputs[0]


def _execute_output_convert(self) -> None:
    parquet_list = find_file(self.work_dir, "parquet")
    for file in parquet_list:
        pd.read_parquet(file).to_csv(f"{self.work_dir}/output/{os.path.basename(file).replace('parquet', 'csv')}",
                                     index=False)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"),
                           api_key=os.getenv("ZHIPU_API_KEY"),
                           api_base=os.getenv("ZHIPU_API_BASE"))
    embedding_llm = EmbeddingsZhipuAI(embeddings_name=os.getenv("EMBEDDINGS_NAME"),
                                      api_key=os.getenv("EMBEDDINGS_API_KEY"),
                                      api_base=os.getenv("EMBEDDINGS_API_BASE"))
    database = GraphNeo4j(
        uri=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE")
    )
    engine = GraphragEngine(work_name="离散数学",
                            llm=task_llm,
                            input_type=["txt", "md"],  # 此处可给单个文件类型、文件类型列表
                            input_dir="test_input",  # 此处可给装有文本文件的文件夹路径、单个文件路径、文件路径列表
                            embeddings=embedding_llm,
                            graph_database=database).execute()
