import os
import logging
from google.protobuf.json_format import MessageToDict

from graphmind.service.chat.base import ChatMessage
from graphmind.service.chat.chat import agent_stream, agent_invoke
from graphmind.api.grpc.chat_service import chat_service_pb2, chat_service_pb2_grpc

SERVER_PORT = os.getenv("SERVER_PORT", 50051)

logger = logging.getLogger(__name__)


# GRPC 聊天服务实现
class ChatServiceImpl(chat_service_pb2_grpc.ChatServiceServicer):
    def stream(self, request, context):
        logger.info(f"Receive Stream request: {request}")
        # 模拟流式返回消息
        req_message = _request_to_message(request)
        for chunk in agent_stream(req_message):
            yield _message_to_response(chunk)

    def invoke(self, request, context):
        logger.info(f"Receive Invoke request: {request}")
        # 处理非流式返回消息
        req_message = _request_to_message(request)
        return _message_to_response(agent_invoke(req_message))

class ChatStatusServiceImpl(chat_service_pb2_grpc.ChatStatusServiceServicer):
    def control(self, request, context):
        logger.info(f"Receive Control request: {request}")
        return chat_service_pb2.Empty()

    def report(self, request, context):
        logger.info(f"Receive Report request: {request}")
        return chat_service_pb2.Empty()

def _request_to_message(request):
    return ChatMessage.model_validate(MessageToDict(request, use_integers_for_enums=True))


def _message_to_response(message: ChatMessage):
    return chat_service_pb2.ChatMessage(**message.model_dump(by_alias=True))
