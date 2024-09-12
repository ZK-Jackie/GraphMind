import neo4j
import json
import uuid
import warnings
from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase, Driver
from typing import List, Dict

from graphmind.adapter.structure import InfoTreeTask, BaseTaskResult, BaseTask
from graphmind.adapter.database import BaseGraphDatabase

default_url = "bolt://localhost:7687"
default_username = "neo4j"
default_password = "password"
default_database = "graphrag20240903"


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


class GraphNeo4j(BaseGraphDatabase):
    def search(self, query):
        pass

    _lc_graph_client: Neo4jGraph | None = None
    _graph_client: Driver | None = None

    def __init__(self,
                 uri: str = default_url,
                 username: str = default_username,
                 password: str = default_password):
        self._lc_graph_client = Neo4jGraph(default_url, default_username, default_password, default_database)
        self._graph_client = GraphDatabase.driver(uri, auth=(username, password), database=default_database)

    def destroy(self):
        if self._graph_client:
            self._graph_client.close()
            self._graph_client = None
        if self._lc_graph_client:
            self._lc_graph_client = None

    def persist(self, tasks: BaseTaskResult | List[BaseTaskResult] | Dict, **kwargs):
        with self._graph_client.session(
                database=default_database,
                default_access_mode=neo4j.WRITE_ACCESS
        ) as session:
            tx = session.begin_transaction()
            for task in tasks:
                if task.task_status == "SUCCESS":
                    for node_name in task.task_result.entity:
                        task.task_result.entity[node_name]["name"] = node_name
                        temp_cypher = get_merge_node_cypher("知识实体", task.task_result.entity[node_name])
                        self._tx_execute_cypher(tx, temp_cypher)
                    for node1_name in task.task_result.relation:
                        for relation in task.task_result.relation[node1_name]:
                            temp_cyphers = get_merge_relation_cypher(node1_name=node1_name,
                                                                     node1_type="知识实体",
                                                                     relation_name=relation,
                                                                     node2_names=task.task_result.relation[node1_name][relation],
                                                                     node2_type="知识实体")
                            self._tx_execute_cypher(tx, temp_cyphers)
            tx.commit()
            print("Transaction committed")
        pass

    @staticmethod
    def _tx_execute_cypher(tx, cypher_str: List[str] | str):
        return
        if type(cypher_str) is str:
            cypher_str = [cypher_str]
        for cypher in cypher_str:
            tx.run(cypher)

    def persist_work_dir(self, work_dir: str, **kwargs):
        if not work_dir:
            raise ValueError("No work_dir provided")
        else:
            # 读取结果文件
            raw_result = []
            # 检查文件是否存在
            try:
                with open(f"{work_dir}/result.json", "r", encoding="utf-8") as f:
                    # 检查json是否合法
                    try:
                        raw_result = json.load(f)
                    except json.JSONDecodeError:
                        warnings.warn(f"Result file in {work_dir} is not a valid json file!")
            except FileNotFoundError:
                warnings.warn(f"No result file found in {work_dir}!")
            # 转换文件
            final_result = []
            for item in raw_result:
                final_result.append(InfoTreeTask.from_dict(item))
            # 移交给正常的persist函数
            self.persist(final_result)
        return self

    def execute_build(self, states: List[CypherNodeState | CypherRelationState]):
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

    async def a_execute_build(self, states: List[CypherNodeState | CypherRelationState]):
        self.execute_build(states)


def get_merge_node_cypher(node_type: str, node_attr: dict):
    """
    EXAMPLE:
    1. 主键约束
    CREATE CONSTRAINT ON (p:Person) ASSERT p.email IS UNIQUE;
    2. 创建、合并节点
    MERGE (p:Person {email: 'example@email.com'})
    ON CREATE SET p.name = 'New Person', p.age = 30
    ON MATCH
        SET p.name = toString(p.name) + ' Updated Person'
        SET p.age = toString(p.age) + '35'
    """
    # 1. 生成第一行，设置节点的uid和name
    line1_attr_str = f"uid: \"{str(uuid.uuid4())}\", name: \"{node_attr['name']}\""
    line1 = f"MERGE (p:{node_type} {{{line1_attr_str}}})"
    # 2. 生成第二行，设置节点的其他属性
    line2_attr_str = ', '.join([f"p.{str(key)} = \"{str(value)}\"" for key, value in node_attr.items() if key != "name" and key != "uid"])
    line2 = f"ON CREATE SET {line2_attr_str}"
    # 3. 生成第三行，设置节点的合并属性
    line3_attr_str = ', '.join([f"p.{str(key)} = toString(p.{str(key)}) + \n \"{str(value)}\"" for key, value in node_attr.items() if key != "name" and key != "uid"])
    line3 = f"ON MATCH SET {line3_attr_str}"
    # 最终整合
    final_cypher = f"{line1} {line2} {line3}"
    print(final_cypher)
    return final_cypher

def get_merge_relation_cypher(node1_name: str, node1_type: str,
                              relation_name: str, node2_names: List[str] | str,
                              node2_type: str) -> List[str]:
    merge_ral_template = "MERGE (a:{node1_type} {{name: '{node1_name}'}}) MERGE (b:{node2_type} {{name: '{node2_name}'}}) MERGE (a)-[r:{relation_name}]->(b)"
    if type(node2_names) is str:
        node2_names = [node2_names]
    merge_ral_list = []
    for node2_name in node2_names:
        merge_ral_list.append(merge_ral_template.format(node1_type=node1_type, node1_name=node1_name,
                                                        relation_name=relation_name, node2_name=node2_name,
                                                        node2_type=node2_type))
    print(merge_ral_list)
    return merge_ral_list


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
