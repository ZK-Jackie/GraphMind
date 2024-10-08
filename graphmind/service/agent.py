import os
from uuid import uuid4
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from graphmind.adapter.database import GraphNeo4j
from graphmind.service.agent_build.graph_agent import GraphAgent
from graphmind.service.agent_build.sub_graphs.cypher_graph import CypherGraph
from graphmind.service.base import ChatMessage
from graphmind.service.context_manager import ContextManager
from graphmind.utils.neo4j_query.base import CypherRelation

load_dotenv()

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
    database=os.getenv("NEO4J_DATABASE"),
    debug=True
)
test_message = ChatMessage(
    role=0,
    content="请总结一下我前面提到的知识点。",
    chunk_resp=True,
    user_id="test",
    conv_id="1",
    message_id=str(uuid4())
)
# 如果用 agent，一定要用项目的 ContextManager 在这里设置 session_id
ContextManager.set_transient_context("session_id", f"{test_message.user_id}_{test_message.conv_id}")

agent = GraphAgent(llm=llm, embeddings=embeddings, database=database)


__all__ = ["agent"]