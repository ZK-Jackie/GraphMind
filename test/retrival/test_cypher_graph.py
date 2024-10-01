import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from graphmind.adapter.database import GraphNeo4j
from graphmind.service.agent_build.base import QueryState
from graphmind.service.agent_build.sub_graphs.cypher_graph import CypherGraph
from graphmind.service.context_manager import ContextManager

llm = ChatOpenAI(
    temperature=0.1,
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

ContextManager.set_transient_context("user_id", "1")
ContextManager.set_transient_context("llm", llm)
ContextManager.set_transient_context("embeddings", embeddings)
ContextManager.set_transient_context("database", database)

agent = CypherGraph(llm=llm, embeddings=embeddings, database=database).agent_with_history
input_state = {
    "raw_queries": ["离散数学是什么", "闭包有哪些关联点"],
    "ask_human": False,
    "entity_finished": False,
    "type_finished": False
}
user_config = {"configurable": {"thread_id": "1"}}
result: QueryState = agent.invoke(input_state, user_config, stream_mode="values", debug=True)
print(type(result))
