from graphmind.adapter.database import GraphNeo4j
from graphmind.core.base import get_default_database

neo4j_client: GraphNeo4j = get_default_database()


__all__ = ["neo4j_client"]