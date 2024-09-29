import asyncio
import os

from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing_extensions import Self, Literal

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from graphmind.adapter.database import GraphNeo4j
from graphmind.service.agent_build.base import QueryState
from graphmind.utils.neo4j_query.entity_extract import batch_entity_llm_extract, batch_entity_database_query
from graphmind.utils.neo4j_query.graph_qa import batch_cypher_query
from graphmind.utils.neo4j_query.type_classify import batch_type_classify
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
    database=os.getenv("NEO4J_DATABASE")
)


@tool(parse_docstring=True)
async def knowledge_search_tool(queries: list[str]) -> str:
    """Useful when you need to know about the knowledge entities that user mentioned in the queries.

    Args:
        queries: A list of simple queries string from user, containing concrete knowledge entities and no reference items.
    """
    pass


class CypherGraph(BaseModel):
    llm: ChatOpenAI | None = Field(description="OpenAI chat model", default=None)
    embeddings: OpenAIEmbeddings | None = Field(description="OpenAI embeddings model", default=None)
    database: GraphNeo4j | None = Field(description="Graph database connection information", default=None)

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
            self._condition_human_topn,
            {"human": "entity_decision_human", "top_n": "entity_decision_top_n"}
        )
        cypher_graph_builder.add_edge("entity_decision_human", "cypher_query")
        cypher_graph_builder.add_edge("entity_decision_top_n", "cypher_query")
        cypher_graph_builder.add_edge("type_classifier", "cypher_query")

        memory = MemorySaver()
        self.agent_with_history = cypher_graph_builder.compile(checkpointer=memory)

        return self

    @staticmethod
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
        query_entity = {}
        if state["raw_queries"]:
            extract_result = asyncio.run(batch_entity_llm_extract(llm, state["raw_queries"]))
            for query, result in zip(state["raw_queries"], extract_result):
                query_entity[query] = result
        else:
            query_entity = {}
        return {"query_entity": query_entity}

    @staticmethod
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
            temp_candidates = asyncio.run(batch_entity_database_query(database, extract_result_list))
            for query, result in zip(query_entity.keys(), temp_candidates):
                query_entity[query] = result
        else:
            query_entity = {}
        return {"query_entity": query_entity}

    @staticmethod
    def _condition_human_topn(state: QueryState) -> Literal["human", "top_n"]:
        if state["ask_human"]:
            return "human"
        else:
            return "top_n"

    @staticmethod
    def _human_entity_decision(state: QueryState) -> QueryState:
        """
        节点位置：进入 CypherGraph START 后的左分支（实体提取）第三节点，决策情况 1。
        前置状态：当前 state 中应当有 query_entity 字典，字典已经完善，拥有子问题句 -> 实体、候选实体列表的映射。
        节点任务：在本节点中，会向 Java 端发送决策请求，随后结束节点。整体工作流会停滞在本节点过后，直至另一函数继续推进下去。

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
        return {"query_entity": query_entity}

    @staticmethod
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
        type_classifier = {}
        if state["raw_queries"]:
            classify_result = asyncio.run(batch_type_classify(llm, state["raw_queries"]))
            for query, result in zip(state["raw_queries"], classify_result):
                type_classifier[query] = result
        else:
            type_classifier = {}
        return {"query_type": type_classifier}

    @staticmethod
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
        retrival_result = []
        if state["query_type"] and state["query_entity"]:
            temp_entities = [entity_list for _, entity_list in state["query_entity"].items()]
            temp_types = [query_type for _, query_type in state["query_type"].items()]
            retrival_result = asyncio.run(batch_cypher_query(database, temp_entities, temp_types))
        else:
            retrival_result = []
        return {"retrival_result": retrival_result}


if __name__ == "__main__":
    subgraph = CypherGraph(llm=llm, embeddings=embeddings, database=database)
    input_state = {
        "raw_queries": ["离散数学是什么", "闭包有哪些关联点"],
        "ask_human": False
    }
    user_config = {"configurable": {"thread_id": "1"}}
    subgraph.agent_with_history.invoke(input_state, user_config, stream_mode="values", debug=True)
