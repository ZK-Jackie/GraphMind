import os
from typing import Generator
from typing_extensions import Self
from uuid import uuid4
from dotenv import load_dotenv

from pydantic import BaseModel, Field, ConfigDict, model_validator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, ConfigurableFieldSpec
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_redis import RedisChatMessageHistory

from graphmind.service.prompts import rag as prompts
from graphmind.adapter.database import GraphNeo4j
from graphmind.service.base import ChatMessage, RoleEnum
from graphmind.service.config.redis import RedisConfig
from graphmind.utils.neo4j_query.graph_qa import get_graph_context

load_dotenv()


class GraphChain(BaseModel):
    llm: ChatOpenAI | None = Field(description="OpenAI chat model", default=None)
    embeddings: OpenAIEmbeddings | None = Field(description="OpenAI embeddings model", default=None)
    database: GraphNeo4j | None = Field(description="Graph database connection information", default=None)

    chain_with_history: RunnableWithMessageHistory | None = Field(description="Chat chain with message history",
                                                                  default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def create_chain(self) -> Self:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompts.system_prompt),
                MessagesPlaceholder(variable_name="history"),
                ("human", prompts.user_prompt_template),
            ]
        )
        parser = StrOutputParser()
        chain = prompt | self.llm | parser
        self.chain_with_history = RunnableWithMessageHistory(
            chain,  # LLMChain
            _get_message_history,  # MessageHistory
            input_messages_key="input",  # Input key in prompt template
            history_messages_key="history",  # History key in prompt template
            history_factory_config=[  # config in MessageHistory
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for a user.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="conv_id",
                    annotation=str,
                    name="Conversation ID",
                    description="Unique identifier for the conversation.",
                    default="",
                    is_shared=True,
                ),
            ],
        )
        return self

    def invoke(self, message: ChatMessage) -> ChatMessage:
        ai_message = ChatMessage(
            role=RoleEnum.AI.value,
            content="",
            chunk_resp=False,
            user_id=message.user_id,
            conv_id=message.conv_id,
            message_id=str(uuid4())
        )
        ai_message.content = self.chain_with_history.invoke(
            input={
                "input": message.content,
                "context": get_graph_context(self.llm, self.embeddings,
                                             self.database,
                                             message.content)
            },
            config={
                "configurable": {"user_id": message.user_id,
                                 "conv_id": message.conv_id}
            })
        return ai_message

    def stream(self, message: ChatMessage) -> Generator[ChatMessage, None, None]:
        ai_message = ChatMessage(
            role=RoleEnum.AI.value,
            content="",
            chunk_resp=message.chunk_resp,
            user_id=message.user_id,
            conv_id=message.conv_id,
            message_id=str(uuid4())
        )
        chunks = self.chain_with_history.stream(
            input={
                "input": message.content,
                "context": get_graph_context(self.llm, self.embeddings,
                                             self.database,
                                             message.content)},
            config={
                "configurable": {"user_id": message.user_id,
                                 "conv_id": message.conv_id}
            })
        for chunk in chunks:
            if message.chunk_resp:
                ai_message.content = chunk
            else:
                ai_message.content += chunk
            yield ai_message


def _get_message_history(user_id: str, conv_id: str) -> RedisChatMessageHistory:
    session_id = f"{user_id}_{conv_id}"
    return RedisChatMessageHistory(session_id=session_id,
                                   redis_url=RedisConfig.REDIS_URL,
                                   ttl=RedisConfig.TTL)


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
    database=os.getenv("NEO4J_DATABASE"),
    debug=True
)
rag_chain = GraphChain(llm=llm, embeddings=embeddings, database=database)

__all__ = ["rag_chain"]
