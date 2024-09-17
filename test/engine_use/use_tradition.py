import os

from graphmind.adapter.database import GraphNeo4j
from graphmind.adapter.engine import TraditionEngine
from graphmind.adapter.llm import TaskZhipuAI
from graphmind.utils.text_reader.markdown import MarkdownReader

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    # 方式1
    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"), api_key=os.getenv("ZHIPU_API_KEY"))
    task_reader = MarkdownReader(file="ch1.md", skip_mark="<abd>")
    engine = TraditionEngine(llm=task_llm, reader=task_reader).execute()
    print(f"Process finished, you can check the result in {engine.work_dir}")
    neo4j_db = GraphNeo4j()
    engine.persist_db(neo4j_db)

    # 方式2
    neo4j_db = GraphNeo4j()
    neo4j_db.persist_work_dir("work_dir/20240903203841")