import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field, ConfigDict, model_validator

from graphmind.adapter.database import GraphNeo4j
from graphmind.adapter.engine.chunk import GraphragEngine
from graphmind.adapter.llm import TaskZhipuAI, EmbeddingsZhipuAI


class GraphEngine(BaseModel):
    """
    GraphMind engine，使用 adapter.engine 执行任务
    """

    llm: ChatOpenAI | None = Field(description="OpenAI chat model", default=None)
    """OpenAI 聊天模型"""

    embeddings: OpenAIEmbeddings | None = Field(description="OpenAI embeddings model", default=None)
    """OpenAI 嵌入模型"""

    database: GraphNeo4j | None = Field(description="Graph database connection information", default=None)
    """图数据库连接信息"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """模型配置"""

    def run(self,
            input_dir: str,
            input_type: list[str],
            work_name: str,
            engine_type: str = "graphrag") -> None:
        """
        运行引擎
        """
        engine = GraphragEngine(llm=self.llm,
                                embeddings=self.embeddings,
                                graph_database=self.database,
                                input_dir=input_dir,
                                input_type=input_type,
                                work_name=work_name)
        engine.execute()
