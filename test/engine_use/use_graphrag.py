import os

from graphmind.adapter.engine import GraphragEngine
from graphmind.adapter.llm import TaskZhipuAI, EmbeddingsZhipuAI

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"), api_key=os.getenv("ZHIPU_API_KEY"))
    embedding_llm = EmbeddingsZhipuAI(embeddings_name=os.getenv("ZHIPU_LLM_NAME"),
                                      api_key=os.getenv("ZHIPU_API_KEY"),
                                      api_base=os.getenv("EMBEDDINGS_API_BASE"))
    # 这里好奇怪，为什么 pycharm 老是警告 api_base 是意外实参？
    engine = GraphragEngine(llm=task_llm, input_dir="input").execute()