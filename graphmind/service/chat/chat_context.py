from graphmind.service.chat.base import ChatMessage
from graphmind.service.context_manager import ContextManager
from graphmind.service.user.user_model import UserModelConfig


def set_user_config(user_config: UserModelConfig):
    ContextManager.set_transient_context("user_config", user_config)


def get_user_config() -> UserModelConfig:
    ret = ContextManager.get_transient_context("user_config")
    return ret


def set_user_message(user_message: ChatMessage):
    ContextManager.set_transient_context("user_message", user_message)


def get_user_message() -> ChatMessage:
    ret = ContextManager.get_transient_context("user_message")
    return ret
