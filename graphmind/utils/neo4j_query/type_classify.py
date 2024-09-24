from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from graphmind.utils.neo4j_query.prompts import classify as prompts


class QueryTypeResult:
    query_type: int | None
    query_cypher: str | None

    def __init__(self,
                 query_type: str | int | None = None,
                 query_cypher: str | None = None):
        self.query_type = int(query_type)
        self.query_cypher = query_cypher


async def type_classify(llm: ChatOpenAI,
                            user_query: str) -> QueryTypeResult | None:
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
    return QueryTypeResult(query_type=obj)
