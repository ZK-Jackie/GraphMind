from dotenv import load_dotenv

from graphmind.core.base import GraphmindModel, get_default_llm, get_default_embeddings, get_default_database
from graphmind.adapter.engine.hierarchy.engine import HierarchyEngine
from graphmind.adapter.reader.markdown import MarkdownReader

if __name__ == '__main__':
    """
    使用前，请在根目录下创建.env文件，提供以下必备内容：
    1. ZHIPU_LLM_NAME="..." 使用的llm模型名称
    2. ZHIPU_API_KEY="..." 使用的llm模型api_key
    3. ZHIPU_API_BASE="..." 使用的llm模型base_url
    """
    load_dotenv()

    models = GraphmindModel(llm=get_default_llm(),
                            llm_batch_size=20,
                            embeddings=get_default_embeddings(),
                            database=get_default_database(debug=True))
    reader = MarkdownReader(file="test_input", skip_mark="<abd>", file_title="离散数学")

    engine = HierarchyEngine(models=models, reader=reader, work_name="离散数学")

    engine.execute()
