import json

from pydantic import BaseModel, Field, field_serializer, ConfigDict

"""
双向链表，绘制查询结果图
"""


class CypherResult(BaseModel):
    cypher: str | None = Field(default=None)
    node_name: str | None = Field(default=None)
    name_embedding: list[float] | None = Field(default=None, exclude=True)
    node_description: str | None = Field(default=None)
    description_embedding: list[float] | None = Field(default=None, exclude=True)
    node_attr: dict | None = Field(default=None)
    related_nodes: list["RelatedNode"] | None = Field(default=[])

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def rag_json_stringify(self) -> str:
        temp_dict = {
            "node_name": self.node_name,
            "node_description": self.node_description,
            "node_attr": self.node_attr,
        }
        return json.dumps(temp_dict, ensure_ascii=False)

    def rag_json_dict(self) -> dict:
        return {
            "node_name": self.node_name,
            "node_description": self.node_description,
            "node_attr": self.node_attr,
        }


class CypherNode:
    pass


class CypherRelation:
    pass


class RelatedNode(BaseModel):
    relation_name: str | None = Field(default=None)
    relation_description: str | None = Field(default=None)
    description_embedding: list[float] | None = Field(default=None)
    previous_cypher_result: CypherResult | None = Field(default=None)
    next_cypher_result: CypherResult | None = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __iter__(self):
        return iter([self.previous_cypher_result, self.next_cypher_result])

    def rag_json_stringify(self):
        temp_dict = {
            "start_node": self.previous_cypher_result.node_name,
            "end_node": self.next_cypher_result.node_name,
            "relation_name": self.relation_name,
            "relation_description": self.relation_description,
        }
        return json.dumps(temp_dict, ensure_ascii=False)

    def rag_json_dict(self):
        return {
            "start_node": self.previous_cypher_result.node_name,
            "end_node": self.next_cypher_result.node_name,
            "relation_name": self.relation_name,
            "relation_description": self.relation_description,
        }
