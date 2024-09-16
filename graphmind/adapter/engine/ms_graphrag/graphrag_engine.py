import os
import time
import warnings
import asyncio

from typing_extensions import Self

from pydantic import model_validator, Field

from graphrag.config import GraphRagConfig
from graphrag.index.api import build_index
from graphrag.index.progress.load_progress_reporter import load_progress_reporter

from graphmind.adapter.engine import BaseEngine
from graphmind.adapter.engine.ms_graphrag.custom_config import CustomGraphRagConfig
from graphmind.adapter.llm import TaskZhipuAI, EmbeddingsZhipuAI


class GraphragEngine(BaseEngine):

    input_dir: str = Field(description="Input file directory")
    graphrag_config: GraphRagConfig | None = Field(description="GraphRag configuration", default=None)
    config_path: str | None = Field(description="Custom configuration file path", default="default/default.yaml")

    @model_validator(mode="after")  # 由于是after模式，字段已经初始化，此处就可以使用self了
    def validate_environment(self) -> Self:
        # 1 检测是否提供了 work_dir
        self.work_dir = self.work_dir or f"{os.getcwd()}/work_dir/{time.strftime('%Y%m%d%H%M%S')}"
        # 2 检测是否提供了 input_dir
        self.input_dir = self.input_dir or os.getenv("INPUT_DIR")
        if not self.input_dir:
            raise ValueError("Please provide the input directory.")
        # 3 配置文件修改
        self.graphrag_config = CustomGraphRagConfig(base_config_dir=self.config_path,
                                                    root_dir=os.path.dirname(os.path.abspath(__file__)),
                                                    llm=self.llm,
                                                    embeddings=self.embeddings,
                                                    input_dir=self.input_dir,
                                                    base_work_dir=self.work_dir).get_graphrag_config()
        return self     # 一定不要忘记返回self！！

    # 运行+插入数据库，结束
    def execute(self, **kwargs):
        # 1 检查是不是openai类的模型
        if not isinstance(self.llm, TaskZhipuAI):
            warnings.warn("GraphRAG Engine only accept OpenAI api like llm.")
        # 2 运行 GraphRAG
        run_id = time.strftime("%Y%m%d-%H%M%S")
        progress_reporter = load_progress_reporter("rich")
        outputs = asyncio.run(
            build_index(config=self.graphrag_config, run_id=run_id, is_resume_run=False,
                        progress_reporter=progress_reporter)
        )

        return self


    def persist_local(self):
        pass


    def persist_database(self):
        pass


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"), api_key=os.getenv("ZHIPU_API_KEY"))
    embedding_llm = EmbeddingsZhipuAI(embeddings_name=os.getenv("ZHIPU_LLM_NAME"),
                                      api_key=os.getenv("ZHIPU_API_KEY"),
                                      api_base=os.getenv("EMBEDDINGS_API_BASE"))
    engine = GraphragEngine(llm=task_llm, input_dir="input").execute()
