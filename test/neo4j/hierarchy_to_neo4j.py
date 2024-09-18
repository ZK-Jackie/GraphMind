import uuid
from neo4j import GraphDatabase
from tqdm import tqdm
import re
import csv
import json

HIERARCHY_NODE = "D:\\Projects\\PycharmProjects\\GraphMind\\test\\result\\glm-4-flash\\final_entity.csv"
HIERARCHY_RELATION = "D:\\Projects\\PycharmProjects\\GraphMind\\test\\result\\glm-4-flash\\final_relation.csv"

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"
NEO4J_DATABASE = "discrete-math-flash"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD), database=NEO4J_DATABASE)


def create_node_cypher(row) -> str:
    # 定义基本模板
    base_template = "CREATE (n:{type} {{{attributes}}})"
    attr_template = "{key}: {value}"
    # 取出attributes字段
    fixes_content = fix_single_quote(row['attribute'])
    attributes = json.loads(fixes_content)
    # 补充名字属性和uid
    attributes['name'] = row['entity']
    attributes['uid'] = str(uuid.uuid4())
    attributes['level'] = row['level']
    attributes['source'] = row['source']
    # 生成属性字符串
    attr_str = ""
    for key, value in attributes.items():
        if isinstance(value, str):
            value = f'"{value}"'
        attr_str += attr_template.format(key=key, value=value) + ", "
    # 去掉最后一个逗号和空格
    attr_str = attr_str[:-2]
    # 生成cypher
    cypher = base_template.format(type=row['type'], attributes=attr_str)
    # print(cypher)
    return cypher


def create_relation_cypher(row) -> str:
    # 定义基本模板
    base_template = "MATCH (a),(b) WHERE a.name = \"{start_name}\" AND b.name = \"{end_name}\" CREATE (a)-[r:RELATED {{name:\"{name}\", desc:\"{description}\"}}]->(b)"
    # 生成cypher
    cypher = base_template.format(
        start_name=row['start'],
        end_name=row['target'],
        name=row['relation'],
        description=row['description'],
    )
    # print(cypher)
    return cypher


def fix_single_quote(file_content):
    # 全部双引号转为 \" 单引号不管
    file_content = re.sub(r'(?<!\\)\"', r'\"', file_content)
    # 全部None转为null
    file_content = re.sub(r'None', r'null', file_content)
    # 全部单引号转为双引号
    file_content = re.sub(r'\'', r'"', file_content)
    return file_content


# 读取CSV文件并导入Neo4j
def node_csv_to_neo4j(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        with driver.session() as session:
            for row in csv_reader:
                # 解析attribute字段的JSON字符串
                try:
                    cypher = create_node_cypher(row)
                    session.run(cypher)
                except Exception as e:
                    print(f"error entity:{row['entity']}, reason:{e}")
                    continue


def relation_csv_to_neo4j(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        with driver.session() as session:
            for row in csv_reader:
                # 检查实体是否存在
                check_query = "MATCH (a {name: $start_name}), (b {name: $end_name}) RETURN a, b"
                result = session.run(check_query, start_name=row['start'], end_name=row['target'])
                if result.single() is None:
                    print(f"Entities not found for relation: {row['start']} -> {row['target']}")
                    continue
                # 解析attribute字段的JSON字符串
                try:
                    cypher = create_relation_cypher(row)
                    session.run(cypher)
                except Exception as e:
                    print(f"error entity:{row['start']} -> {row['target']}, reason:{e}")
                    continue


def add_level_attr(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        with driver.session() as session:
            for row in csv_reader:
                query = "MATCH (n) WHERE n.name = $name SET n.level = $level"
                session.run(query, name=row['entity'], level=row['level'])


def add_source_attr(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        with driver.session() as session:
            for row in csv_reader:
                query = "MATCH (n) WHERE n.name = \"{name}\" SET n.source = \"{source}\""
                session.run(query.format(name=row['entity'], source=row['source']))


# 调用函数，传入你的CSV文件路径
# node_csv_to_neo4j(HIERARCHY_NODE)
# relation_csv_to_neo4j(HIERARCHY_RELATION)
# add_level_attr(HIERARCHY_NODE)
# add_source_attr(HIERARCHY_NODE)

# 关闭数据库连接
driver.close()
