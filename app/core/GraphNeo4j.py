import neo4j
from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase, Driver
from typing import List
import uuid

default_url = "bolt://localhost:7687"
default_username = "neo4j"
default_password = "password"


class CypherNodeState:
    uid: uuid.UUID
    node_type: str
    node_attr: dict

    def __init__(self, node_type: str, node_attr: dict, uid: uuid.UUID = None):
        if uid is None:
            uid = uuid.uuid4()
        self.node_type = node_type
        self.node_attr = node_attr
        self.node_attr["uid"] = uid

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
    node2_name: str

    def __init__(self, node1_name: str, relation_name: str, node2_name: str):
        self.node1_name = node1_name
        self.node2_name = node2_name
        self.relation_name = relation_name

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


class GraphNeo4j:
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

    def _execute_build(self, states: List[CypherNodeState|CypherRelationState]):
        # 创建会话，一个with就是一个事务
        with self._graph_client.session(
            database="neo4j",
            default_access_mode=neo4j.WRITE_ACCESS
        ) as session:
            tx = session.begin_transaction()
            try:
                # TODO 插入节点、关系
                pass
            except Exception as e:
                tx.rollback()
                raise e
            tx.commit()
            print("Transaction committed")



def _create_node(tx, node_type: str, node_attr: dict):
    if "uid" not in node_attr:
        node_attr["uid"] = uuid.uuid4()
    tx.run(f"CREATE (:{node_type} {node_attr})")
