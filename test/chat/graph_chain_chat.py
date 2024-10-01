import os
from uuid import uuid4

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from graphmind.adapter.database import GraphNeo4j
from graphmind.service.base import ChatMessage
from graphmind.service.chain import GraphChain

if __name__ == "__main__":
    llm = ChatOpenAI(
        temperature=0.8,
        api_key=os.getenv("ZHIPU_API_KEY"),
        model_name=os.getenv("ZHIPU_LLM_NAME"),
        base_url=os.getenv("ZHIPU_API_BASE"),
    )
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDINGS_NAME1"),
        openai_api_base=os.getenv("EMBEDDINGS_API_BASE1"),
        openai_api_key=os.getenv("EMBEDDINGS_API_KEY1")
    )
    database = GraphNeo4j(
        uri=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE")
    )
    chat = GraphChain(llm=llm, embeddings=embeddings, database=database)
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
    for res in chat.stream(test_message):
        print(res.content, end="")