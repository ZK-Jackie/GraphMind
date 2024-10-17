from graphmind.serve_api import serve
from main import logger_init

logger_init()
serve(serve="grpc", port=8081)