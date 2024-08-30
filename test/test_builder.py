"""
GraphBuilder类将会是用户使用本程序的核心类之一，用户将会通过这个类来构建知识图谱。
下文在演示怎么用这个类来构建知识图谱。
"""
import os
from zhipuai import ZhipuAI
from dotenv import load_dotenv
from chatkg.core.GraphBuilder import GraphBuilder
from chatkg.adapter.database.GraphNeo4j import GraphNeo4j

load_dotenv()

zhipu_client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))
graph_builder = (GraphBuilder(file="ch1.md",
                              engine="tradition")
                 .build(skip_mark="<abd>",
                        llm=zhipu_client,
                        model="glm-4-0520")
                 )
# graph_builder = GraphBuilder(engine="tradition").load("temp/20240830205230/result.json")
graph = GraphNeo4j()
graph_builder.persist(graph_client=graph)