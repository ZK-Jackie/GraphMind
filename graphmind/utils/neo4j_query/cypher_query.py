import json


class CypherResult:
    cypher: str | None = None
    node_name: str | None = None
    name_embedding: list[float] | None = None
    node_description: str | None = None
    description_embedding: list[float] | None = None
    node_attr: dict | None = None
    related_nodes: list["RelatedNode"] | None = None

    def __init__(self,
                 cypher: str | None = None,
                 node_name: str | None = None,
                 name_embedding: list[float] | None = None,
                 node_description: str | None = None,
                 description_embedding: list[float] | None = None,
                 node_attr: dict | None = None,
                 related_nodes: list["RelatedNode"] | None = None):
        if related_nodes is None:
            related_nodes = []
        self.cypher = cypher

        self.node_name = node_name
        self.name_embedding = name_embedding

        self.node_description = node_description
        self.description_embedding = description_embedding

        self.node_attr = node_attr

        self.related_nodes = related_nodes

    def rag_json_stringify(self):
        temp_dict = {
            "node_name": self.node_name,
            "node_description": self.node_description,
            "node_attr": self.node_attr,
        }
        return json.dumps(temp_dict, ensure_ascii=False, indent=0)

    def rag_json_dict(self):
        return {
            "node_name": self.node_name,
            "node_description": self.node_description,
            "node_attr": self.node_attr,
        }

class CypherNode:
    pass

class CypherRelation:
    pass

class RelatedNode:
    relation_name: str | None = None
    relation_description: str | None = None
    description_embedding: list[float] | None = None
    previous_cypher_result: CypherResult | None = None # 对于
    next_cypher_result: CypherResult | None = None

    def __init__(self,
                 related_name: str | None,
                 related_description: str | None,
                 description_embedding: CypherResult | None = None,
                 previous_cypher_result: CypherResult | None = None,
                 next_cypher_result: CypherResult | None = None):
        self.relation_name = related_name
        self.relation_description = related_description
        self.description_embedding = description_embedding
        self.previous_cypher_result = previous_cypher_result
        self.next_cypher_result = next_cypher_result

    def __iter__(self):
        return iter([self.previous_cypher_result, self.next_cypher_result])

    def rag_json_stringify(self):
        temp_dict = {
            "start_node": self.previous_cypher_result.node_name,
            "end_node": self.next_cypher_result.node_name,
            "relation_name": self.relation_name,
            "relation_description": self.relation_description,
        }
        return json.dumps(temp_dict, ensure_ascii=False, indent=0)

    def rag_json_dict(self):
        return {
            "start_node": self.previous_cypher_result.node_name,
            "end_node": self.next_cypher_result.node_name,
            "relation_name": self.relation_name,
            "relation_description": self.relation_description,
        }
