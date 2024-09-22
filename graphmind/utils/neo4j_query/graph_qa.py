import asyncio
import os
import warnings
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pydantic import Field

from graphmind.adapter.database import GraphNeo4j
from graphmind.utils.neo4j_query import BaseQA
from graphmind.utils.neo4j_query.cyphers.cypher_template import SingleNodeTemplate, MultiNodeTemplate, \
    OverallNodeTemplate
from graphmind.utils.neo4j_query.entity_extract import entity_extract, EntityExtractResult
from graphmind.utils.neo4j_query.type_classify import type_classify, QueryTypeResult
import prompts.rag as prompts


# TODO Chain 模式下的 GraphQA

# TODO Tool 模式下的 GraphQA

class GraphQA(BaseQA):
    database: GraphNeo4j | None = Field(description="Database connection", default=None)
    history_storage: str | None = Field(description="History storage", default=None)

    @property
    def rag_llm(self) -> Runnable:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompts.system_prompt),
                ("user", prompts.user_prompt_template)
            ]
        )
        parser = StrOutputParser()
        chain = prompt | llm | parser
        return chain

    def invoke(self, query: str) -> list[Any] | str | Any:
        # TODO 0 问题分块

        # 1 寻找实体，确定类别
        async def extract_classify() -> tuple[list[EntityExtractResult] | Any, QueryTypeResult | Any]:
            tasks = [
                entity_extract(self.llm, self.embeddings, self.database, query),
                type_classify(self.llm, query)
            ]
            results = await asyncio.gather(*tasks)
            return results[0], results[1]

        extraction, classify = asyncio.run(extract_classify())
        # 2 构造查询，执行查询，获取查询结果
        graph_result = cypher_query(self.database, extraction, classify)
        print(f"graph_result: {graph_result}")
        # 3 构造 prompt，返回llm结果
        return self.rag_llm.invoke({"input": query, "context": graph_result})

    def invoke_with_message(self, session_id: Any, query: str) -> str:
        pass

    def search(self, query: str) -> str:
        pass

def cypher_query(database: GraphNeo4j,
                 entity_result: list[EntityExtractResult],
                 query_type: QueryTypeResult) -> str | None:
    # 前期变量准备
    entity_list = [entity.final_entity for entity in entity_result] # 待被查询的实体列表
    print(f"type: {query_type.query_type}")
    # 执行查询、结果获取、prompt构造
    if query_type.query_type == 1:
        return SingleNodeTemplate.run_cypher_query(database, entity_list)
        # return OverallNodeTemplate.run_cypher_query(database, entity_list)
    elif query_type.query_type == 2:
        return MultiNodeTemplate.run_cypher_query(database, entity_list)
    elif query_type.query_type == 3:
        return OverallNodeTemplate.run_cypher_query(database, entity_list)
    else:
        warnings.warn(f"Query type not supported.")
        return None


if __name__ == "__main__":
    # from graphmind.adapter.database import Neo4jDatabase
    from dotenv import load_dotenv

    load_dotenv()
    llm = ChatOpenAI(
        temperature=0.8,
        api_key=os.getenv("ZHIPU_API_KEY"),
        model_name=os.getenv("ZHIPU_LLM_NAME"),
        base_url=os.getenv("ZHIPU_API_BASE"),
    )
    embeddings = OpenAIEmbeddings(
        model=os.getenv("EMBEDDINGS_NAME1"),
        openai_api_base=os.getenv("EMBEDDINGS_API_BASE1"),
        openai_api_key=os.getenv("EMBEDDINGS_API_KEY1")
    )
    database = GraphNeo4j(
        uri=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE"),
        debug=True
    )
    qa = GraphQA(llm=llm, embeddings=embeddings, database=database)
    print(qa.invoke("形式演算系统的类别有哪几个？"))
