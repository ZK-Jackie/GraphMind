import uuid
from neo4j import GraphDatabase
from tqdm import tqdm
import re
import csv
import json

HIERARCHY_NODE = "D:\\Projects\\PycharmProjects\\GraphMind\\results\\deep_clean_result\\glm-4-plus\\final_entity.csv"
HIERARCHY_RELATION = "D:\\Projects\\PycharmProjects\\GraphMind\\results\\deep_clean_result\\glm-4-plus\\base_relation.csv"

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"
NEO4J_DATABASE = "neo4j"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD), database=NEO4J_DATABASE)


def create_node_cypher(row) -> str:
    # 定义基本模板
    base_template = "CREATE (n:{type} {{{attributes}}})"
    attr_template = "{key}: {value}"
    # 取出类型字段
    type_str = row['type'][1:-1]
    # 取出attributes字段
    attributes = json.loads(row['attributes'])
    # 补充名字属性和uid
    attributes['name'] = row['name'][1:-1]
    attributes['uid'] = str(uuid.uuid4())
    attributes['level'] = int(row['level'])
    attributes['source'] = str(json.loads(row['source']))
    # 生成属性字符串
    attr_str = ""
    for key, value in attributes.items():
        if isinstance(value, str):
            value = f'"{value}"'
        attr_str += attr_template.format(key=key, value=value) + ", "
    # 去掉最后一个逗号和空格
    attr_str = attr_str[:-2]
    # 生成cypher
    cypher = base_template.format(type=type_str, attributes=attr_str)
    print(cypher)
    return cypher


def create_relation_cypher(row) -> str:
    # 定义基本模板，当存在时，合并description字段，中间用换行符分隔
    base_template = """
    MATCH (a {{name: "{start_name}"}}), (b {{name: "{end_name}"}})
    MERGE (a)-[r:{name}]->(b)
    ON CREATE SET r.description = "{description}"
    ON MATCH SET r.description = r.description + "\\n" + "{description}"
    SET r.source = {source}
    """
    # 生成cypher
    cypher = base_template.format(
        start_name=row['start'][1:-1],
        end_name=row['end'][1:-1],
        name=row['relation'][1:-1],
        description=row['description'][1:-1],
        source=str(json.loads(row['source']))
    )
    cypher.replace("\"", "\\\"")
    cypher.replace("\'", "\\\'")
    cypher.replace("\\\\", "\\")
    cypher.replace("\\", "\\\\")
    print(cypher)
    return cypher


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
                    print(f"error entity:{row['name']}, reason:{e}")
                    continue


def relation_csv_to_neo4j(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        with driver.session() as session:
            for row in csv_reader:
                start_name = row['start'][1:-1]
                end_name = row['end'][1:-1]
                # 检查实体是否存在
                check_query = "MATCH (a {name: $start_name}), (b {name: $end_name}) RETURN a, b"
                result = session.run(check_query, start_name=start_name, end_name=end_name)
                if result.single() is None:
                    print(f"Entities not found for relation: {start_name} -> {end_name}")
                    continue
                # 解析attribute字段的JSON字符串
                try:
                    cypher = create_relation_cypher(row)
                    session.run(cypher)
                except Exception as e:
                    print(f"error entity:{start_name} -> {end_name}, reason:{e}")
                    continue


# 调用函数，传入你的CSV文件路径
node_csv_to_neo4j(HIERARCHY_NODE)
relation_csv_to_neo4j(HIERARCHY_RELATION)

# 关闭数据库连接
driver.close()
