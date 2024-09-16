from pydantic import BaseModel, Field

from graphmind.adapter.engine.base import BaseEntity, BaseRelation


class GmEntity(BaseEntity):
    type: str | None = Field(description="Entity type", default=None)
    """实体类型"""

    name: str | None = Field(description="Entity name", default=None)
    """实体名字"""

    attributes: dict | None = Field(description="Entity attributes", default=None)
    """实体属性"""

    def dump_dict(self):
        return {
            "type": self.type,
            "name": self.name,
            "attributes": self.attributes
        }

class GmRelation(BaseRelation):
    node1: str | None = Field(description="Node1 name", default=None)
    """节点1名字"""

    node2: str | None = Field(description="Node2 name", default=None)
    """节点2名字"""

    relation_name: str | None = Field(description="Relation name", default=None)
    """关系名字"""

    description: str | None = Field(description="Relation description", default=None)
    """关系描述"""

    attributes: dict | None = Field(description="Relation attributes", default=None)
    """关系属性"""

    def dump_dict(self):
        return {
            "name": self.name,
            "attributes": self.attributes
        }