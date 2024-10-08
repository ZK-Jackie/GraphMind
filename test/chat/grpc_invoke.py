# 测试stream接口
import grpc

from graphmind.api.grpc.chat_service import chat_service_pb2_grpc, chat_service_pb2

if __name__ == '__main__':
    with grpc.insecure_channel('8.138.154.191:50051') as channel:
        stub = chat_service_pb2_grpc.ChatServiceStub(channel)
        response = stub.invoke(chat_service_pb2.ChatMessage(
            role=0,
            content="你好！",
            chunkResp=True,
            userId="Test",
            convId="1",
            messageId="Test"
        ))
        print(response)