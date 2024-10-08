from graphmind.api.grpc.graph_service import graph_service_pb2_grpc, graph_service_pb2

class GraphServiceImpl(graph_service_pb2_grpc.GraphServiceServicer):
    def build(self, request, context):
        """
        构建图谱
        Args:
            request: 构建请求
            context: 上下文

        Returns:
            build_status: 构建状态

        """
