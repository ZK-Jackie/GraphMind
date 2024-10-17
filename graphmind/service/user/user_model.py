import logging

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field

from graphmind.core.base import GraphmindModelConfig, LLMConfig, EmbeddingsConfig
from graphmind.service.context_manager import ContextManager
from graphmind.service.databases.redis_db import redis_client

logger = logging.getLogger(__name__)


class UserModelConfig(BaseModel):
    """
    用户模型配置
    """
    user_id: str | None = Field(description="User ID", default=None)
    """用户ID"""

    conv_id: str | None = Field(description="Conversation ID", default=None)
    """对话ID"""

    graphmind_config: GraphmindModelConfig | None = Field(description="Graphmind 模型配置", default=None)
    """Graphmind配置"""

    @property
    def config_redis_title(self):
        return "model-config"

    @property
    def config_key(self) -> str:
        """
        Redis key
        """
        return UserModelConfig.get_config_key(self.user_id, self.conv_id)

    @property
    def session_id(self) -> str:
        """
        Session ID
        """
        return UserModelConfig.get_session_id(self.user_id, self.conv_id)

    @staticmethod
    def get_config_key(user_id: str, conv_id: str) -> str:
        """
        获取Redis key
        """
        return f"model-config:user-{user_id}_conv-{conv_id}"

    @staticmethod
    def get_session_id(user_id: str, conv_id: str) -> str:
        """
        获取Session ID
        """
        return f"user-{user_id}_conv-{conv_id}"

    @staticmethod
    def get_tool_session_id(user_id: str, conv_id: str, tool_id: str) -> str:
        """
        获取工具Session ID
        """
        return f"user-{user_id}_conv-{conv_id}_tool-{tool_id}"


def context_user_config() -> UserModelConfig:
    """
    从上下文中获取用户模型配置
    Returns:
        UserModelConfig: 用户模型配置

    """
    return ContextManager.get_transient_context("user_config")


def context_session_id() -> str:
    """
    从上下文中获取 session_id
    Returns:
        str: session_id

    """
    return context_user_config().session_id


def context_llm() -> ChatOpenAI:
    """
    从上下文中获取 LLM
    Returns:
        ChatOpenAI: LLM

    """
    return ChatOpenAI(**context_llm_config().model_dump())


def context_llm_config() -> LLMConfig:
    """
    从上下文中获取 LLM 配置
    Returns:
        LLMConfig: LLM 配置

    """
    return context_user_config().graphmind_config.llm


def context_embeddings() -> OpenAIEmbeddings:
    """
    从上下文中获取 Embeddings
    Returns:
        OpenAIEmbeddings: Embeddings

    """
    return OpenAIEmbeddings(**context_embeddings_config().model_dump())


def context_embeddings_config() -> EmbeddingsConfig:
    """
    从上下文中获取 Embeddings 配置
    Returns:
        EmbeddingsConfig: Embeddings 配置

    """
    return context_user_config().graphmind_config.embeddings


def context_graphmind_config() -> GraphmindModelConfig:
    """
    从上下文中获取 Graphmind 配置
    Returns:
        GraphmindModelConfig: Graphmind 配置

    """
    return context_user_config().graphmind_config


def get_model_config(user_id: str, conv_id) -> UserModelConfig:
    """
    获取用户模型配置
    """
    try:
        user_json_from_redis = redis_client.get(UserModelConfig.get_config_key(user_id, conv_id))
    except Exception as e:
        logger.warning(f"No user model config from redis: {e}, user_id: {user_id}, conv_id: {conv_id}")
        user_json_from_redis = None
    if user_json_from_redis:
        return UserModelConfig.model_validate_json(user_json_from_redis)
    return UserModelConfig(user_id=user_id, conv_id=conv_id)


def save_model_config(user_model_config: UserModelConfig) -> None:
    """
    保存用户模型配置
    """
    redis_client.set(user_model_config.config_key,
                     user_model_config.model_dump())
