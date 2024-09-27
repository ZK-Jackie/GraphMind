import asyncio
import warnings
from typing_extensions import Self

from langchain_community.graphs import Neo4jGraph
from pydantic import model_validator

from graphmind.adapter.database import BaseGraphDatabase


class GraphNeo4j(BaseGraphDatabase):
    debug: bool = False
    _client: Neo4jGraph | None = None

    @model_validator(mode="after")
    def validate_env(self) -> Self:
        try:
            self._client = Neo4jGraph(url=self.uri,
                                      username=self.username,
                                      password=self.password,
                                      database=self.database)
        except Exception as e:
            if self.debug:
                return self
            else:
                warnings.warn(f"Neo4j connection failed.")
                raise RuntimeError("Neo4j connection failed.")
        return self

    def query(self, query: str) -> list[dict] | None:
        return self._client.query(query)

    async def aquery(self, query: str) -> list[dict] | None:
        return self.query(query)

    async def batch(self, cyphers: list[str]) -> list[list[dict]] | None:
        tasks = [self.aquery(cypher) for cypher in cyphers]
        resp = await asyncio.gather(*tasks)
        return resp
