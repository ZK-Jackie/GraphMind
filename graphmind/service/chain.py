import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from graphmind.adapter.database import GraphNeo4j
from graphmind.service.chat import GraphChat

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
rag_chain = GraphChat(llm=llm, embeddings=embeddings, database=database)

__all__ = ["rag_chain"]