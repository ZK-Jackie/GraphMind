from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from graphmind.adapter.database import GraphNeo4j
from graphmind.core.base import LLMConfig, EmbeddingsConfig, GraphDBConfig


def get_model_from_config(config):
    if isinstance(config, LLMConfig):
        return ChatOpenAI(**config.model_dump())
    elif isinstance(config, EmbeddingsConfig):
        return OpenAIEmbeddings(**config.model_dump())
    elif isinstance(config, GraphDBConfig):
        return GraphNeo4j(**config.model_dump())

    return None