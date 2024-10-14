import argparse
import logging
import os

from graphmind.serve_api import serve
from graphmindui.start_gui import start_ui


def logger_init():
    # 创建日志目录
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging.basicConfig(
        level=logging.DEBUG,  # 日志级别
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
        handlers=[
            logging.FileHandler('logs/application.log', mode='a'),  # 输出到文件
            logging.StreamHandler()  # 输出到控制台
        ]
    )

    # 初始化日志汇报
    logging.info('Logging initialized')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # 定义 serve 子命令
    parser_serve = subparsers.add_parser("serve", help="Serve mode")
    parser_serve.add_argument("--mode", type=str, help="Serve mode", choices=["grpc", "restful"], default="grpc")
    parser_serve.add_argument("--host", type=str, help="Host to serve on", default="127.0.0.1")
    parser_serve.add_argument("--port", type=int, help="Port to serve on", default=50051)

    parser_gui = subparsers.add_parser("ui", help="GUI mode")
    parser_gui.add_argument("--mode", type=str, help="GUI mode", choices=["qt"], default="qt")

    args = parser.parse_args()
    logger_init()
    if args.serve and args.ui:
        raise ValueError("Cannot serve and start GUI at the same time.")
    if args.serve:
        serve(mode=args.mode, host=args.host, port=args.port)
    if args.ui:
        start_ui(mode=args.mode)
