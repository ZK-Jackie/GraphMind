# import sys
# # 动态添加项目根目录到 PYTHONPATH
# sys.path.append("D:\\Projects\\PycharmProjects\\GraphMind")


import os

from graphmind.adapter.database import GraphNeo4j
from graphmind.adapter.engine.chunk import GraphragEngine
from graphmind.adapter.llm import TaskZhipuAI, EmbeddingsZhipuAI

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"),
                           api_key=os.getenv("ZHIPU_API_KEY"),
                           api_base=os.getenv("ZHIPU_API_BASE"))
    embedding_llm = EmbeddingsZhipuAI(embeddings_name=os.getenv("EMBEDDINGS_NAME"),
                                      api_key=os.getenv("EMBEDDINGS_API_KEY"),
                                      api_base=os.getenv("EMBEDDINGS_API_BASE"))
    database = GraphNeo4j(
        uri=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE")
    )
    engine = GraphragEngine(llm=task_llm,
                            input_type=["txt", "md"],   # 此处可给单个文件类型、文件类型列表
                            input_dir="test_input",  # 此处可给装有文本文件的文件夹路径、单个文件路径、文件路径列表
                            embeddings=embedding_llm,
                            graph_database=database).execute()