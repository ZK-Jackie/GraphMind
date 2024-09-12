"""
知识图谱检索器
"""
from pydantic import BaseModel

from graphmind.adapter.database import BaseGraphDatabase

class GraphRetrieval(BaseModel):
    db: BaseGraphDatabase | None = None

    def search(self, query):
        # 搜索
        return self.db.search(query)

    def destroy(self):
        self.db.destroy()

    def entity_extraction(self, query):
        # 实体提取
        # return self.db.entity_extraction(query)
        pass