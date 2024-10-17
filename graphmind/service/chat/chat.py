import logging

from graphmind.core.base import GraphmindModelConfig

from graphmind.service.chat.base import ChatMessage
from graphmind.service.chat.chat_agent.agent import agent
from graphmind.service.chat.chat_chain.chain import chain
from graphmind.service.chat.chat_context import set_user_config, set_user_message
from graphmind.service.user.user_model import get_model_config

logger = logging.getLogger(__name__)


def agent_stream(human_message: ChatMessage):
    # 1 获取用户配置
    user_config = get_model_config(human_message.user_id, human_message.conv_id)
    # 2 检查用户配置状态
    if user_config.graphmind_config is None:
        user_config.graphmind_config = GraphmindModelConfig()
    # 3 将用户信息存入上下文管理器
    set_user_config(user_config)
    set_user_message(human_message)
    logger.info(f"user config is set: {user_config}")
    # 4 调用 Agent
    for ai_message in agent.stream(human_message):
        yield ai_message


def agent_invoke(human_message: ChatMessage) -> ChatMessage:
    # 1 获取用户配置
    user_config = get_model_config(human_message.user_id, human_message.conv_id)
    # 2 检查用户配置状态
    if user_config.graphmind_config is None:
        user_config.graphmind_config = GraphmindModelConfig()
    # 3 将用户信息存入上下文管理器
    set_user_config(user_config)
    set_user_message(human_message)
    logger.info(f"user config is set: {user_config}")
    # 4 调用 Agent
    return agent.invoke(human_message)


def chain_stream(human_message: ChatMessage):
    # 1 获取用户配置
    user_config = get_model_config(human_message.user_id, human_message.conv_id)
    # 2 检查用户配置状态
    if user_config.graphmind_config is None:
        user_config.graphmind_config = GraphmindModelConfig()
    # 3 将用户信息存入上下文管理器
    set_user_config(user_config)
    set_user_message(human_message)
    logger.info(f"user config is set: {user_config}")
    # 4 调用 Chain
    for ai_message in chain.stream(human_message):
        yield ai_message


def chain_invoke(human_message: ChatMessage) -> ChatMessage:
    # 1 获取用户配置
    user_config = get_model_config(human_message.user_id, human_message.conv_id)
    # 2 检查用户配置状态
    if user_config.graphmind_config is None:
        user_config.graphmind_config = GraphmindModelConfig()
    # 3 将用户信息存入上下文管理器
    set_user_config(user_config)
    set_user_message(human_message)
    logger.info(f"user config is set: {user_config}")
    # 4 调用 Chain
    return chain.invoke(human_message)


__all__ = ["agent_stream", "agent_invoke", "chain_stream", "chain_invoke"]
