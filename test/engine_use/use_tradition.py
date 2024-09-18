import os

from graphmind.adapter.engine.hierarchy import TraditionEngine
from graphmind.adapter.llm import TaskZhipuAI
from graphmind.utils.text_reader.markdown import MarkdownReader

if __name__ == '__main__':
    task_llm = TaskZhipuAI(llm_name=os.getenv("ZHIPU_LLM_NAME"),
                           api_key=os.getenv("ZHIPU_API_KEY"),
                           llm_kwargs={
                               'temperature': 0.1,
                           },
                           json_output=True)
    task_reader = MarkdownReader(file="input", skip_mark="<abd>")
    # 此处可给单个文件路径、文件路径列表、装有文件的文件夹路径
    # 此处可以设定若某段文本包含某个标记（这里设为<abd>）则跳过读取该段。若设定的是标题，则跳过整个章节
    engine = TraditionEngine(llm=task_llm, reader=task_reader, struct_type="tree").execute()
    # 此处就暂时固定是这样写，别的还没做
    print(f"Process finished, you can check the result in {engine.work_dir}")
