from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

from graphmind.utils.neo4j_query.entity_extract import EntityExtractResult


def reduce_messages(left: list, right: list) -> list:
    return add_messages(left, right)


class State(TypedDict):
    messages: Annotated[list, reduce_messages]  # 消息列表
    ask_human: bool  # 是否需要人工干预
    override_message: bool  # 是否需要覆盖最新的 AI 消息


def reduce_query_type(left: int, right: int) -> int:
    return right


def reduce_query_state(left: dict, right: dict) -> dict:
    return right


def reduce_result_state(left: list, right: list) -> list:
    return right


class QueryState(TypedDict):
    messages: Annotated[list, reduce_messages]  # 从主 Agent 中继承下来的消息列表
    raw_queries: list[str]
    query_entity: Annotated[dict[str, list[EntityExtractResult] | None], reduce_query_state]
    query_type: Annotated[dict[str, int], reduce_query_state]
    query_cypher: Annotated[dict[str, str], reduce_query_state]
    retrival_result: Annotated[list[str], reduce_result_state]
    entity_finished: bool
    type_finished: bool
    ask_human: bool
