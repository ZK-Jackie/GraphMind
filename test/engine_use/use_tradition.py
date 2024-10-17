import os

from graphmind.adapter.reader.markdown import MarkdownReader
from graphmind.adapter.engine.hierarchy.engine import HierarchyEngine
from graphmind.core.base import GraphmindModel, get_default_llm, get_default_embeddings, get_default_database

from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()

    models = GraphmindModel(llm=get_default_llm(),
                            llm_batch_size=os.getenv("LLM_CONCUR_NUM", 20),
                            task_buffer_size=os.getenv("TASK_BUFFER_SIZE", 32),
                            embeddings=get_default_embeddings(),
                            database=get_default_database(debug=True))
    reader = MarkdownReader(file="test_input", skip_mark="<abd>", file_title="离散数学")

    engine = HierarchyEngine(models=models, reader=reader, work_name="离散数学")

    engine.execute()
