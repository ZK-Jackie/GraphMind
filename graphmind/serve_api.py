"""
两种启动模式，gRPC 接口调用 grpc/grpc_run.py，http 的用 fastapi 或预计还是使用 gRPC 做
"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def serve(**kwargs):
    """
    Serve API.
    Args:
        **kwargs:
        - 必须包含`serve`字段，值为`grpc`或`restful`；
        - 可选包含`port`字段，值为端口号

    Returns:
        None
    """
    global logger

    def serve_restful():
        import uvicorn
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from graphmind.api.v1.chat import api_chat
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.include_router(api_chat)
        SERVER_PORT = kwargs.get("port") or os.getenv("SERVER_PORT", 8080)
        uvicorn.run("main:app", host="0.0.0.0", port=SERVER_PORT, reload=True)

    def serve_grpc():
        import grpc
        from concurrent import futures
        from graphmind.api.grpc.chat_service import chat_service_pb2_grpc
        from graphmind.api.grpc.status_service import status_service_pb2_grpc
        from graphmind.api.grpc.impl.chat_service_impl import ChatServiceImpl, ChatStatusServiceImpl
        from graphmind.api.grpc.impl.status_service_impl import StatusServiceImpl
        from dotenv import load_dotenv
        load_dotenv()
        SERVER_PORT = kwargs.get("port") or os.getenv("SERVER_PORT", 50051)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chat_service_pb2_grpc.add_ChatServiceServicer_to_server(ChatServiceImpl(), server)
        chat_service_pb2_grpc.add_ChatStatusServiceServicer_to_server(ChatStatusServiceImpl(), server)
        status_service_pb2_grpc.add_StatusServiceServicer_to_server(StatusServiceImpl(), server)
        logger.info(f"Service added to server.")
        server.add_insecure_port(f'[::]:{SERVER_PORT}')
        server.start()
        logger.info(f"Server started at port {SERVER_PORT}.")
        server.wait_for_termination()

    if kwargs.get("serve") == "grpc":
        serve_grpc()
    elif kwargs.get("serve") == "restful":
        serve_restful()
    else:
        raise ValueError("Invalid serve mode.")
