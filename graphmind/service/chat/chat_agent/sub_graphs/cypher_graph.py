import asyncio
import logging

from typing_extensions import Self, Literal

from pydantic import BaseModel, Field, model_validator, ConfigDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from graphmind.service.chat.chat_agent.base import QueryState, State
from graphmind.service.chat.chat_agent.redis_memory import redis_saver
from graphmind.service.chat.chat_reporter import status_report
from graphmind.service.databases.neo4j_db import neo4j_client
from graphmind.service.user.user_model import context_llm_config, context_llm, context_session_id
from graphmind.utils.neo4j_query.entity_extract import batch_entity_llm_extract, batch_entity_database_query
from graphmind.utils.neo4j_query.graph_qa import batch_cypher_query
from graphmind.utils.neo4j_query.type_classify import batch_type_classify

logger = logging.getLogger(__name__)


class CypherGraph(BaseModel):
    agent_with_history: CompiledStateGraph | None = Field(description="Chat agent with message history",
                                                          default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def create_agent(self) -> Self:
        cypher_graph_builder = StateGraph(QueryState)

        cypher_graph_builder.add_node("entity_extraction", self._llm_entity_extract)
        cypher_graph_builder.add_node("entity_candidate", self._database_entity_candidate)
        cypher_graph_builder.add_node("entity_decision_human", self._human_entity_decision)
        cypher_graph_builder.add_node("entity_decision_top_n", self._top_n_entity_decision)
        cypher_graph_builder.add_node("type_classifier", self._type_classifier)
        cypher_graph_builder.add_node("cypher_query", self._cypher_query)

        cypher_graph_builder.add_edge(START, "entity_extraction")
        cypher_graph_builder.add_edge(START, "type_classifier")
        cypher_graph_builder.add_edge("entity_extraction", "entity_candidate")

        cypher_graph_builder.add_conditional_edges(
            "entity_candidate",
            self._condition_human_top_n,
            {"human": "entity_decision_human", "top_n": "entity_decision_top_n"}
        )

        cypher_graph_builder.add_conditional_edges(
            "entity_decision_human",
            self._condition_cypher_query,
            {"cypher_query": "cypher_query", "__end__": "__end__"}
        )
        cypher_graph_builder.add_conditional_edges(
            "entity_decision_top_n",
            self._condition_cypher_query,
            {"cypher_query": "cypher_query", "__end__": "__end__"}
        )
        cypher_graph_builder.add_conditional_edges(
            "type_classifier",
            self._condition_cypher_query,
            {"cypher_query": "cypher_query", "__end__": "__end__"}
        )

        self.agent_with_history = cypher_graph_builder.compile(checkpointer=redis_saver)

        logger.info("CypherGraph agent created.")

        return self

    @staticmethod
    @status_report("分析问询实体")
    def _llm_entity_extract(state: QueryState):
        """
        节点位置：进入 CypherGraph START 后的左分支（实体提取）第一节点。
        前置状态：当前 state 中仅有 queries 字段，需要构造 query_entity 字段。
        节点任务：在本节点中，将会负责调用 LLM 执行实体提取任务。

        Args:
            state: LangGraph 数据流状态

        Returns:
            state: LangGraph 数据流状态
        """
        # 从上下文中获取 LLM
        llm_config = context_llm_config()
        llm = ChatOpenAI(**llm_config.model_dump())
        query_entity = {}
        if state["raw_queries"]:
            extract_result = asyncio.run(batch_entity_llm_extract(llm, state["raw_queries"]))
            for query, result in zip(state["raw_queries"], extract_result):
                query_entity[query] = result
        else:
            query_entity = {}
        logger.info(f"Extracted entities: {query_entity}")
        return {"query_entity": query_entity}

    @staticmethod
    @status_report("查询数据库实体")
    def _database_entity_candidate(state: QueryState):
        """
        节点位置：进入 CypherGraph START 后的左分支（实体提取）第二节点。
        前置状态：当前 state 中应当有 query_entity 字典，需要为每一个值构造 entity_candidate 字段。
        节点任务：在本节点中，将会负责调用 neo4j 数据库执行实体提取任务。

        Args:
            state: LangGraph 数据流状态

        Returns:
            state: LangGraph 数据流状态
        """
        query_entity = state["query_entity"]
        if query_entity:
            extract_result_list = [entity_list for _, entity_list in query_entity.items()]
            temp_candidates = asyncio.run(batch_entity_database_query(neo4j_client, extract_result_list))
            for query, result in zip(query_entity.keys(), temp_candidates):
                query_entity[query] = result
        else:
            query_entity = {}
        logger.info(f"Extracted candidates: {query_entity}")
        return {"query_entity": query_entity}

    @staticmethod
    @status_report("实体筛选")
    def _condition_human_top_n(state: QueryState) -> Literal["human", "top_n"]:
        if state["ask_human"]:
            return "human"
        else:
            return "top_n"

    @staticmethod
    @status_report("等待人工干预")
    def _human_entity_decision(state: QueryState) -> QueryState:
        """
        节点位置：进入 CypherGraph START 后的左分支（实体提取）第三节点，决策情况 1。
        前置状态：当前 state 中应当有 query_entity 字典，字典已经完善，拥有子问题句 -> 实体、候选实体列表的映射。
        节点任务：在本节点中，会向 Java 端发送决策请求，随后结束节点。整体工作流会停滞在本节点过后，直至另一个函数继续推进下去。

        Args:
            state: LangGraph 数据流状态

        Returns:
            state: LangGraph 数据流状态
        """
        pass

    @staticmethod
    def _top_n_entity_decision(state: QueryState):
        """
        节点位置：进入 CypherGraph START 后的左分支（实体提取）第三节点，决策情况 2。
        前置状态：当前 state 中应当有 query_entity 字典，字典已经完善，拥有子问题句 -> 实体、候选实体列表的映射。
        节点任务：在本节点中，会使用 top_n 策略确定实体，并将结果保存在 query_entity 字典中。

        Args:
            state: LangGraph 数据流状态

        Returns:
            state: LangGraph 数据流状态

        """
        query_entity = state["query_entity"]
        if query_entity:
            for query, extract_result in query_entity.items():
                for entity_result in extract_result:
                    entity_result.final_entity = entity_result.candidate[0].cypher_candidate.node_name
        else:
            query_entity = {}
        logger.info(f"Top N entities: {query_entity}")
        return {"query_entity": query_entity, "entity_finished": True}

    @staticmethod
    @status_report("分析问询类型")
    def _type_classifier(state: QueryState):
        """
        节点位置：进入 CypherGraph START 后的右分支（类型分类）第一节点。
        前置状态：当前 state 中仅有 queries 字段，需要根据 queries 字段得到 query_type 对照字典。
        节点任务：在本节点中，会调用 neo4j 数据库执行实体类型分类任务。

        Args:
            state: LangGraph 数据流状态

        Returns:
            state: LangGraph 数据流状态
        """
        llm = context_llm()
        type_classifier = {}
        if state["raw_queries"]:
            classify_result = asyncio.run(batch_type_classify(llm, state["raw_queries"]))
            for query, result in zip(state["raw_queries"], classify_result):
                type_classifier[query] = result
        else:
            type_classifier = {}
        logger.info(f"Classified types: {type_classifier}")
        return {"query_type": type_classifier, "type_finished": True}

    @staticmethod
    def _condition_cypher_query(state: QueryState) -> Literal["cypher_query", "__end__"]:
        """
        双分支是否可收束判断
        """
        if state["entity_finished"] and state["type_finished"]:
            return "cypher_query"
        else:
            return "__end__"

    @staticmethod
    @status_report("查询数据库信息")
    def _cypher_query(state: QueryState):
        """
        节点位置：进入 CypherGraph START 后左右分支收束节点。
        前置状态：当前 state 中应当有 query_entity 字典和 query_type 字典，需要根据这两个字典构造 query_cypher 字典。
        节点任务：在本节点中，会调用 neo4j 数据库执行 cypher 查询任务。

        Args:
            state: LangGraph 数据流状态

        Returns:
            state: LangGraph 数据流状态
        """
        if state["query_type"] and state["query_entity"]:
            temp_entities = [entity_list for _, entity_list in state["query_entity"].items()]
            temp_types = [query_type for _, query_type in state["query_type"].items()]
            retrival_result = asyncio.run(batch_cypher_query(neo4j_client, temp_entities, temp_types))
        else:
            retrival_result = []
        logger.info(f"Retrival result: {retrival_result}")
        return {"retrival_result": retrival_result}


@tool(parse_docstring=True)
def knowledge_search_tool(queries: list[str]):
    """Useful when user need to know about the knowledge.

    Args:
        queries: A list of simple queries string from user, containing concrete knowledge entities and no reference items.
    """


class KnowledgeSearch(BaseModel):
    """Useful when user need to know about the knowledge.

    To use this function, give a list of simple queries string from user. You need to eliminate referential pronouns from user's query as much as possible, and turn possible multiple questions into multiple sub-queries.
    """

    queries: list[str]


cypher_agent = CypherGraph()


def knowledge_search_tool_node(main_state: State):
    # 1 从 main_state 中获取 queries 字段
    last_ai_message = main_state["messages"][-1]
    queries = last_ai_message.tool_calls[0]["args"]["queries"]
    tool_call_id = last_ai_message.tool_calls[0]["id"]
    # 2 构造 trigger_state，驱动子图
    trigger_state = {
        "raw_queries": queries,
        "ask_human": False,
        "entity_finished": False,
        "type_finished": False
    }
    # 3 调用子图
    # 从上下文 user_config 中获取 session_id；如果不存在，报错
    session_id = context_session_id()
    if session_id is None:
        raise RuntimeError("Error in validating user configuration.")
    thread_id = f"{session_id or 'test_1'}_{tool_call_id}"
    user_config = {"configurable": {"thread_id": thread_id}}
    agent = cypher_agent.agent_with_history
    result: QueryState = agent.invoke(trigger_state, user_config, stream_mode="values")
    return {"messages": [ToolMessage(content=str(result["retrival_result"]),
                                     tool_call_id=tool_call_id)]}
