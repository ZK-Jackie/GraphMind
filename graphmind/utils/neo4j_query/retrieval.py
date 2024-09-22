from graphmind.utils.neo4j_query.cypher_query import CypherResult
from graphmind.utils.neo4j_query.entity_extract import EntityExtractResult


class GraphRetrieval:
    question_chunk = None
    entity: list[EntityExtractResult] | None = None
    retrieval_type: str | int | None = None
    cypher_query: list[CypherResult] | None = None