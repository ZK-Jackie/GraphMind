import grpc
import logging
import os

from graphmind.api.grpc.chat_service import chat_service_pb2_grpc, chat_service_pb2
from graphmind.service.chat.base import ChatStatus

logger = logging.getLogger(__name__)

JAVA_URL = f"{os.getenv('JAVA_HOST')}:{os.getenv('JAVA_GRPC_PORT')}"


def chat_status_report(chat_status: ChatStatus):
    with grpc.insecure_channel(JAVA_URL) as channel:
        stub = chat_service_pb2_grpc.ChatStatusServiceStub(channel)
        logger.info(f"Report chat status: {chat_status}")
        stub.report(chat_service_pb2.ChatStatus(
            **chat_status.model_dump(by_alias=True)
        ))
