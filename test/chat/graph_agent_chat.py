"""
测试 agent 输出
"""
from uuid import uuid4
from dotenv import load_dotenv

from graphmind.service.chat.chat import agent_stream
from graphmind.service.chat.base import ChatMessage

load_dotenv()

if __name__ == "__main__":
    test_message = ChatMessage(
        role=0,
        content="请总结一下我前面提到的知识点。",
        chunk_resp=True,
        user_id="test",
        conv_id="1",
        message_id=str(uuid4())
    )

    # 方式1：整体输出
    # res = chat.invoke(test_message)
    # print(res)
    # 方式2：流式输出
    for res in agent_stream(test_message):
        print(res.content, end="")