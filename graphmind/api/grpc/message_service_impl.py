import os

from graphmind.service.base import ChatMessage
from graphmind.service.agent import agent
from graphmind.api.grpc.chat_service import chat_service_pb2, chat_service_pb2_grpc

SERVER_PORT = os.getenv("SERVER_PORT", 50051)

from graphmind_logger import logger


# GRPC 聊天服务实现
class MessageServiceImpl(chat_service_pb2_grpc.ChatServiceServicer):
    def stream(self, request, context):
        logger.info(f"Receive Stream request: {request}")
        # 模拟流式返回消息
        req_message = _request_to_message(request)
        for chunk in agent.stream(req_message):
            yield _message_to_response(chunk)

    def invoke(self, request, context):
        logger.info(f"Receive Invoke request: {request}")
        # 处理非流式返回消息
        req_message = _request_to_message(request)
        return _message_to_response(agent.invoke(req_message))


def _request_to_message(request):
    return ChatMessage(
        role=request.role,
        content=request.content,
        chunk_resp=request.chunkResp,
        user_id=request.userId,
        conv_id=request.convId,
        message_id=request.messageId
    )


def _message_to_response(message: ChatMessage):
    return chat_service_pb2.ChatMessage(
        role=message.role,
        content=message.content,
        chunkResp=message.chunk_resp,
        userId=message.user_id,
        convId=message.conv_id,
        messageId=message.message_id
    )
