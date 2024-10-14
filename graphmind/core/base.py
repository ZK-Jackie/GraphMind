import asyncio
import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing_extensions import Self, Literal

from graphmind.adapter.database import GraphNeo4j


class LLMConfig(BaseModel):
    """
    LLM Model Configurations
    经过校验，现有字段名称与 LangChain、OpenAI SDK 完全一致
    """
    temperature: float = Field(description="Temperature for LLM", default=0.8)
    """LLM 温度"""

    max_tokens: int = Field(description="Max tokens for LLM", default=4095)
    """LLM 最大token数"""

    model_name: str = Field(description="Model name for LLM", default="glm-4-flash")
    """LLM 模型名称"""

    openai_api_key: str = Field(description="API key for LLM", default=os.getenv("ZHIPU_API_KEY"))
    """LLM API key"""

    openai_api_base: str = Field(description="Base url for LLM", default=os.getenv("ZHIPU_API_BASE"))
    """LLM base url"""

    extra_config: dict = Field(description="Extra configurations for LLM", default_factory=dict)
    """LLM 其他配置，应当与 LangChain 支持的保持一致"""

    concur_limit: int = Field(description="Concurrent limit for LLM", default=20, exclude=True)
    """LLM 并发限制"""

    debug: bool = Field(description="Debug mode for LLM", default=False)
    """LLM 调试模式"""

    verbose: bool = Field(description="Verbose mode for LLM", default=False)
    """LLM 详细用户控制台输出模式"""

    model_config = ConfigDict(protected_namespaces=())


class EmbeddingsConfig(LLMConfig):
    """
    Embeddings Model Configurations
    """
    model_name: str = Field(description="Model name for embeddings", default="embedding-3")
    """嵌入模型名称"""

    openai_api_key: str = Field(description="API key for embeddings", default=os.getenv("EMBEDDINGS_API_KEY"))
    """嵌入API key"""

    openai_api_base: str = Field(description="Base url for embeddings", default=os.getenv("EMBEDDINGS_API_BASE"))
    """嵌入base url"""

    concur_limit: int = Field(description="Concurrent limit for embeddings", default=1, exclude=True)
    """嵌入并发限制"""

    dimensions: int = Field(description="Dimensions for embeddings generated", default=2048)
    """嵌入维度"""


class GraphDBConfig(BaseModel):
    """
    Graph database configurations
    """
    type: Literal["neo4j", "memgraph"] = Field(description="Type of graph database", default="neo4j")
    """图数据库类型"""

    uri: str | None = Field(description="URI for Neo4j", default=os.getenv("NEO4J_URI"))
    """图数据库 URI"""

    username: str | None = Field(description="Username for Neo4j", default=os.getenv("NEO4J_USER"))
    """图数据库用户名"""

    password: str | None = Field(description="Password for Neo4j", default=os.getenv("NEO4J_PASSWORD"))
    """图数据库密码"""

    database: str | None = Field(description="Database for Neo4j", default=os.getenv("NEO4J_DATABASE"))
    """图数据库名称"""

    debug: bool | None = Field(description="Debug mode for Neo4j", default=False)
    """Neo4j 调试模式"""

    verbose: bool = Field(description="Verbose mode for Neo4j", default=False)
    """Neo4j 详细用户控制台输出模式"""


class GraphmindModelConfig(BaseModel):
    """
    Graphmind Model Configurations
    """
    llm: LLMConfig = Field(description="LLM configurations", default_factory=LLMConfig)
    """LLM 配置"""

    embeddings: EmbeddingsConfig = Field(description="Embeddings configurations", default_factory=EmbeddingsConfig)
    """嵌入配置"""

    database: GraphDBConfig = Field(description="Graph database configurations", default_factory=GraphDBConfig)
    """图数据库配置"""

    @model_validator(mode="before")
    def validate_environment(cls, values: dict) -> dict:
        """
        Validate environment variables
        """
        return values


class GraphmindBaseConfig:
    """
    Graphmind application configurations
    """
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    """应用日志级别"""

    log_path: str = "logs"
    """应用日志路径"""

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    """应用日志格式"""

    log_file_format: str = "%Y-%m-%d.log"
    """应用日志文件名称格式"""


class GraphmindModel(BaseModel):
    """
    GraphMind model
    """
    llm: ChatOpenAI | None = Field(description="OpenAI chat model")
    """OpenAI 聊天模型"""

    llm_batch_size: int = Field(description="Batch size for LLM", default=5)
    """LLM 批处理大小"""

    task_buffer_size: int = Field(description="Task buffer size", default=32)
    """任务缓冲区大小"""

    embeddings: OpenAIEmbeddings | None = Field(description="OpenAI embeddings model")
    """OpenAI 嵌入模型"""

    embeddings_batch_size: int = Field(description="Batch size for embeddings", default=1)
    """嵌入批处理大小"""

    database: GraphNeo4j | None = Field(description="Graph database connection information")
    """图数据库连接信息"""

    llm_semaphore: asyncio.Semaphore | None = Field(description="LLM semaphore", default=None)

    task_semaphore: asyncio.Semaphore | None = Field(description="Program semaphore", default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_connection(self) -> Self:
        """
        Validate connection
        """
        self.llm_semaphore = asyncio.Semaphore(self.llm_batch_size)
        self.task_semaphore = asyncio.Semaphore(2 * self.llm_batch_size)
        return self


def get_default_llm(**kwargs) -> ChatOpenAI:
    """
    Get default model
    """

    return ChatOpenAI(
        temperature=0.1,
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
