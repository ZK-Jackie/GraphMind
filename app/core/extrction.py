from typing import List
from tqdm import tqdm
from app.core.info import InfoNode, InfoTree
import os

from langchain_text_splitters import MarkdownHeaderTextSplitter

from core.info import InfoForest
from utils.FileReader import FileReader


class MarkdownReader(FileReader):
    file: str | List[str]
    skip_mark: str

    def __init__(self,
                 file: str | List[str],
                 skip_mark: str = "<skip>",
                 **kwargs):
        md_file = []
        if file:
            if os.path.isdir(file):
                for root, dirs, files in os.walk(file):
                    for f in files:
                        if f.endswith('.md'):
                            md_file.append(os.path.join(root, f))
            else:
                md_file.append(file)
        if not md_file:
            raise ValueError("No md file or directory provided")
        self.file = md_file
        self.skip_mark = skip_mark

    def indexing(self):
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header1"),
                ("##", "Header2"),
                ("###", "Header3"),
                ("####", "Header4"),
                ("#####", "Header5"),
                ("######", "Header6"),
                ("#######", "Header7"),
                ("########", "Header8")
            ],
            return_each_line=False,
        )

        forest = InfoForest()
        # 1. 逐个处理md文件
        for md in tqdm(self.file, desc="Indexing markdown files"):
            # 打开文件，加载文件内容
            with open(md, "r", encoding="utf-8") as f:
                markdown_text = f.read()
            # 分割/格式化文件内容
            doc_para_list = splitter.split_text(markdown_text)
            # 构造 info 树
            temp_node = None
            tree = InfoTree(
                InfoNode(
                    title="《离散数学》",
                    content=None,
                    parent=None,
                    level=0
                )
            )
            for doc in doc_para_list:
                if self.skip_mark in str(doc.metadata):
                    continue
                # 获得最后一个键值对的键值对应的值
                title_list = list(doc.metadata.keys())
                now_doc_title = doc.metadata[title_list[-1]]
                now_doc_level = len(title_list)
                now_doc_content = doc.page_content
                now_node = InfoNode(
                    title=now_doc_title,
                    content=now_doc_content,
                    level=now_doc_level
                )
                # 给这个 root 只是为了方便插入节点，减缓时间复杂度
                tree.insert_node(temp_node, now_node, now_doc_level)
                temp_node = now_node
            forest.add_tree(tree)
        return forest



if __name__ == "__main__":
    # 1. 创建MarkdownReader对象
    md_reader = MarkdownReader(file="ch1.md", skip_mark="<abd>")
    # 2. 索引文件
    doc_forest = md_reader.indexing()
    # 3. 输出
    for tree in doc_forest.trees:
        for node in tree.traverse(tree.main_root):
            print()
