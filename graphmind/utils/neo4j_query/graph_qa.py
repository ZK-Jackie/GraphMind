import asyncio
import warnings
import logging
from typing import Any

from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from graphmind.adapter.database import GraphNeo4j
from graphmind.utils.neo4j_query.cyphers.cypher_template import SingleNodeTemplate, MultiNodeTemplate, \
    OverallNodeTemplate
from graphmind.utils.neo4j_query.entity_extract import entity_extract, EntityExtractResult
from graphmind.utils.neo4j_query.type_classify import type_classify

logger = logging.getLogger(__name__)


def get_graph_context(llm: ChatOpenAI,
                      embeddings: OpenAIEmbeddings,
                      database: GraphNeo4j,
                      query: str) -> str:
    """
    neo4j_query 主入口，建议结合说明文档中的流程图理解整体流程
    """
    # 步骤1 寻找实体，确定类别
    extraction, classify = asyncio.run(extract_classify(llm, embeddings, database, query))
    # 步骤2 构造查询，执行查询，获取查询结果
    graph_result = cypher_query(database, extraction, classify)
    return graph_result


async def extract_classify(llm: ChatOpenAI,
                           embeddings: OpenAIEmbeddings,
                           database: GraphNeo4j,
                           query: str) -> tuple[list[EntityExtractResult] | Any, int | Any]:
    """
    步骤 1 执行函数
    """
    tasks = [
        entity_extract(llm, embeddings, database, query),
        type_classify(llm, query)
    ]
    results = await asyncio.gather(*tasks)
    return results[0], results[1]


def cypher_query(database: GraphNeo4j,
                 entity_result: list[EntityExtractResult],
                 query_type: int) -> str | None:
    """
    步骤 2 执行函数
    """
    # 前期变量准备
    entity_list = [entity.final_entity for entity in entity_result]  # 待被查询的实体列表
    print(f"type: {query_type}")
    # 执行查询、结果获取、prompt构造
    if query_type == 1:
        return SingleNodeTemplate.run_cypher_query(database, entity_list)
        # return OverallNodeTemplate.run_cypher_query(database, entity_list)
    elif query_type == 2:
        return MultiNodeTemplate.run_cypher_query(database, entity_list)
    elif query_type == 3:
        return OverallNodeTemplate.run_cypher_query(database, entity_list)
    else:
        warnings.warn(f"Query type not supported.")
        return None


async def batch_cypher_query(database: GraphNeo4j,
                             entity_result: list[list[EntityExtractResult]],
                             query_type: list[int]) -> list[str] | tuple[Any] | None:
    """
    步骤 2 异步批量执行函数
    """
    # 前期变量准备
    results = []
    tasks = []
    for entities, query_type in zip(entity_result, query_type):
        entity_list = [entity.final_entity if entity else None for entity in entities]
        if not entity_list:
            continue
        if query_type == 1:
            tasks.append(SingleNodeTemplate.a_run_cypher_query(database, entity_list))
        elif query_type == 2:
            tasks.append(MultiNodeTemplate.a_run_cypher_query(database, entity_list))
        elif query_type == 3:
            tasks.append(OverallNodeTemplate.a_run_cypher_query(database, entity_list))
        else:
            warnings.warn(f"Query type not supported.")
            tasks.append(None)
    results = await asyncio.gather(*tasks)
    logger.info(f"Batch cypher query results: {results}")
    return results
