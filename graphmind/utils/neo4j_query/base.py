from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel, Field, ConfigDict


class BaseQA(BaseModel, ABC):
    llm: ChatOpenAI | None = Field(description="Chat model", default=None)
    embeddings: OpenAIEmbeddings | None = Field(description="Embeddings model", default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def invoke(self, query: str) -> str:
        pass

    @abstractmethod
    def search(self, query: str) -> str:
        pass

