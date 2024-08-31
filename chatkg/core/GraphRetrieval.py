"""
知识图谱检索器
"""
from chatkg.adapter.database import BaseDatabase

class GraphRetrieval:
    db: BaseDatabase | None = None

    def __init__(self, db: BaseDatabase, **kwargs):
        self.db = db

    def search(self, query):
        # 搜索
        return self.db.search(query)

    def destroy(self):
        self.db.destroy()