import os
from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing_extensions import Self

from graphmind.adapter.database import GraphNeo4j


class GraphmindModel(BaseModel):
    """
    GraphMind model
    """
    llm: ChatOpenAI | None = Field(description="OpenAI chat model")
    """OpenAI 聊天模型"""

    llm_batch_size: int = Field(description="Batch size for LLM", default=5)
    """LLM 批处理大小"""

    embeddings: OpenAIEmbeddings | None = Field(description="OpenAI embeddings model")
    """OpenAI 嵌入模型"""

    embeddings_batch_size: int = Field(description="Batch size for embeddings", default=1)
    """嵌入批处理大小"""

    database: GraphNeo4j | None = Field(description="Graph database connection information")
    """图数据库连接信息"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_connection(self) -> Self:
        """
        Validate connection
        """
        return self




def get_default_llm(**kwargs) -> ChatOpenAI:
    """
    Get default model
    """
    return ChatOpenAI(
        temperature=0.8,
        model_name=os.getenv("ZHIPU_LLM_NAME"),
        openai_api_key=os.getenv("ZHIPU_API_KEY"),
        openai_api_base=os.getenv("ZHIPU_API_BASE"),
        **kwargs
    )


def get_default_embeddings(**kwargs) -> OpenAIEmbeddings:
    """
    Get default embeddings
    """
    return OpenAIEmbeddings(
        model=os.getenv("EMBEDDINGS_NAME1"),
        openai_api_base=os.getenv("EMBEDDINGS_API_BASE1"),
        openai_api_key=os.getenv("EMBEDDINGS_API_KEY1"),
        **kwargs
    )


def get_default_database(**kwargs) -> GraphNeo4j:
    """
    Get default database
    """
    return GraphNeo4j(
        uri=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE"),
        **kwargs
    )
