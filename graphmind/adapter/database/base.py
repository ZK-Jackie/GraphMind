"""
数据库类
"""
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, ConfigDict


class BaseGraphDatabase(BaseModel, ABC):
    uri: str = Field(description="The URI of the database", default="bolt://localhost:7687")
    username: str = Field(description="The username of the database", default="neo4j")
    password: str = Field(description="The password of the database", default="password")
    database: str = Field(description="The database name of the database", default="neo4j")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def query(self, query: str):
        pass

    @abstractmethod
    async def aquery(self, query: str):
        pass

    @abstractmethod
    def batch(self, cyphers: list[str]):
        pass
