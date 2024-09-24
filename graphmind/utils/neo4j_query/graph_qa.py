import asyncio
import warnings
from typing import Any

from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from graphmind.adapter.database import GraphNeo4j
from graphmind.utils.neo4j_query.cyphers.cypher_template import SingleNodeTemplate, MultiNodeTemplate, \
    OverallNodeTemplate
from graphmind.utils.neo4j_query.entity_extract import entity_extract, EntityExtractResult
from graphmind.utils.neo4j_query.type_classify import type_classify, QueryTypeResult


def get_graph_context(llm: ChatOpenAI,
                      embeddings: OpenAIEmbeddings,
                      database: GraphNeo4j,
                      query: str) -> str:
    # 1 寻找实体，确定类别
    extraction, classify = asyncio.run(extract_classify(llm, embeddings, database, query))
    # 2 构造查询，执行查询，获取查询结果
    graph_result = cypher_query(database, extraction, classify)
    return graph_result


async def extract_classify(llm: ChatOpenAI,
                           embeddings: OpenAIEmbeddings,
                           database: GraphNeo4j,
                           query: str) -> tuple[list[EntityExtractResult] | Any, QueryTypeResult | Any]:
    tasks = [
        entity_extract(llm, embeddings, database, query),
        type_classify(llm, query)
    ]
    results = await asyncio.gather(*tasks)
    return results[0], results[1]


def cypher_query(database: GraphNeo4j,
                 entity_result: list[EntityExtractResult],
                 query_type: QueryTypeResult) -> str | None:
    # 前期变量准备
    entity_list = [entity.final_entity for entity in entity_result]  # 待被查询的实体列表
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
