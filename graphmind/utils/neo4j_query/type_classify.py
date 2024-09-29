import asyncio
from typing import Any
from enum import Enum

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from graphmind.utils.neo4j_query.prompts import classify as prompts


class QueryType(Enum):
    SINGLE = 1
    """单实体查询"""

    MULTI = 2
    """多实体查询"""

    OVERALL = 3
    """整体查询"""


async def type_classify(llm: ChatOpenAI,
                        user_query: str) -> int | None:
    """
    Classify the query type based on the user query.
    Args:
        llm (ChatOpenAI): Chat model
        user_query (str): User query
    Returns:
        str: Query type
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompts.system_prompt),
            ("user", prompts.user_prompt_template),
        ]
    )
    parser = StrOutputParser()
    chain = prompt | llm | parser
    obj: str = await chain.ainvoke({"input": user_query})
    return int(obj)


async def batch_type_classify(llm: ChatOpenAI,
                              user_queries: list[str]) -> list[int] | tuple[Any] | None:
    """
    Batch classify the query type based on the user queries.
    Args:
        llm (ChatOpenAI): Chat model
        user_queries (list[str]): User queries
    Returns:
        list[str]: Query types
    """
    tasks = [type_classify(llm, query) for query in user_queries]
    return await asyncio.gather(*tasks)
