# import sys
# # 动态添加项目根目录到 PYTHONPATH
# sys.path.append("D:\\Projects\\PycharmProjects\\GraphMind")


import os

from graphmind.adapter.engine.chunk import GraphragEngine
from graphmind.core.base import GraphmindModel, get_default_embeddings, get_default_database, get_default_llm

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    models = GraphmindModel(llm=get_default_llm(),
                            llm_batch_size=os.getenv("LLM_CONCUR_NUM", 20),
                            task_buffer_size=os.getenv("TASK_BUFFER_SIZE", 32),
                            embeddings=get_default_embeddings(),
                            database=get_default_database(debug=True))
    engine = GraphragEngine(models=models,
                            input_type=["txt", "md"],
                            work_name="离散数学", input_dir="test_input").execute()
