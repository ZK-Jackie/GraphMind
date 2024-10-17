"""
测试 chain 输出
"""
from uuid import uuid4

from graphmind.service.chat.base import ChatMessage
from graphmind.service.chat.chat import chain_stream

if __name__ == "__main__":
    test_message = ChatMessage(
        role=0,
        content="我刚才说了什么？",
        chunk_resp=True,
        user_id="test",
        conv_id="1",
        message_id=str(uuid4())
    )
    # 方式1：整体输出
    # res = chat.invoke(test_message)
    # print(res)
    # 方式2：流式输出
    for res in chain_stream(test_message):
        print(res.content, end="")