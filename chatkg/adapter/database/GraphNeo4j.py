from distutils.util import execute

import neo4j
import json
import uuid
import warnings
from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase, Driver
from typing import List

from chatkg.adapter.database.base import BaseDatabase

default_url = "bolt://localhost:7687"
default_username = "neo4j"
default_password = "password"


class CypherNodeState:
    node_type: str
    node_attr: dict

    def __init__(self, node_type: str, node_attr: dict, uid: uuid.UUID = None):
        if uid is None:
            uid = uuid.uuid4()
        if type(node_type) is not str:
            node_type = str(node_type)
            warnings.warn(f"node_type should be str, but got {type(node_type)}")
        if type(node_attr) is not dict:
            node_attr = json.loads(node_attr)
            warnings.warn(f"node_attr should be dict, but got {type(node_attr)}")
        self.node_type = node_type
        self.node_attr = node_attr
        self.node_attr["uid"] = str(uid)

    def get_type(self):
        return self.node_type

    def get_attr(self):
        attr_str = ', '.join([f"'{key}': '{value}'" for key, value in self.node_attr.items()])
        return attr_str

    def __str__(self):
        """
        生成类cypher语句的字符串，只是用于方便阅读调试而存在
        :return: 类cypher语句的字符串
        """
        attr_str = ', '.join([f"'{key}': '{value}'" for key, value in self.node_attr.items()])
        return f"'{self.node_type}' {{{attr_str}}}"

    def __repr__(self):
        """
        生成类cypher语句的字符串，只是用于方便阅读调试而存在
        :return:  类cypher语句的字符串
        """
        return self.__str__()


class CypherRelationState:
    relation_name: str
    node1_name: str
    node1_type: str
    node2_name: str
    node2_type: str

    def __init__(self, node1_name: str, relation_name: str, node2_name: str,
                 node1_type: str, node2_type: str):
        self.node1_name = node1_name
        self.node2_name = node2_name
        self.relation_name = relation_name
        self.node1_type = node1_type
        self.node2_type = node2_type

    def __str__(self):
        """
        生成类cypher语句的字符串，只是用于方便阅读调试而存在
        :return:  类cypher语句的字符串
        """
        return f"{self.node1_name} -[:{self.relation_name}]-> {self.node2_name}"

    def __repr__(self):
        """
        生成类cypher语句的字符串，只是用于方便阅读调试而存在
        :return:  类cypher语句的字符串
        """
        return self.__str__()

    def __hash__(self):
        return hash((self.node1_name, self.relation_name, self.node2_name))

    def __eq__(self, other):
        return self.node1_name == other.node1_name and self.relation_name == other.relation_name and self.node2_name == other.node2_name


class GraphNeo4j(BaseDatabase):
    _lc_graph_client: Neo4jGraph | None = None
    _graph_client: Driver | None = None

    def __init__(self,
                 url: str = default_url,
                 username: str = default_username,
                 password: str = default_password):
        self._lc_graph_client = Neo4jGraph(default_url, default_username, default_password)
        self._graph_client = GraphDatabase.driver(url, auth=(username, password))

    def destroy(self):
        if self._graph_client:
            self._graph_client.close()
            self._graph_client = None
        if self._lc_graph_client:
            self._lc_graph_client = None

    def execute_build(self, states: List[CypherNodeState|CypherRelationState]):
        # 创建会话，一个with就是一个事务
        with self._graph_client.session(
            database="neo4j",
            default_access_mode=neo4j.WRITE_ACCESS
        ) as session:
            tx = session.begin_transaction()
            try:
                if states:
                    for state in states:
                        if "CypherNodeState" in str(type(state)):
                            _create_node(tx, state)
                        elif "CypherRelationState" in str(type(state)):
                            _create_relation(tx, state)
                else:
                    warnings.warn("No states to execute")
                pass
            except Exception as e:
                tx.rollback()
                raise e
            tx.commit()
            print("Transaction committed")

    async def a_execute_build(self, states: List[CypherNodeState|CypherRelationState]):
        self.execute_build(states)


def _create_node(tx, state: CypherNodeState):
    if "uid" not in state.node_attr:
        state.node_attr["uid"] = uuid.uuid4()
    node_attr_str = ', '.join([f"{str(key)}: \"{str(value)}\"" for key, value in state.node_attr.items()])
    # TODO 插入节点优化，想优化成 tx.run(base_str, dict)的形式
    print(f"CREATE (:{state.node_type} {{{node_attr_str}}})")
    tx.run(f"CREATE (:{state.node_type} {{{node_attr_str}}})")

def _create_relation(tx, state: CypherRelationState):
    node1_name = state.node1_name
    node2_name = state.node2_name
    relation_name = state.relation_name
    node1_type = state.node1_type
    node2_type = state.node2_type

    create_relation_str = f"MATCH (a:{node1_type} {{name: '{node1_name}'}}), (b:{node2_type} {{name: '{node2_name}'}}) CREATE (a)-[r:{relation_name}]->(b)"
    # TODO 插入节点优化，想优化成 tx.run(base_str, dict)的形式
    print(create_relation_str)
    tx.run(create_relation_str)