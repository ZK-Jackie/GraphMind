from graphmind.adapter.database import BaseGraphDatabase


class GraphChaoxing(BaseGraphDatabase):
    def __init__(self, config):
        pass

    def search(self, query):
        pass

    def destroy(self):
        pass

    def execute_build(self, states):
        pass

    async def a_execute_build(self, states):
        pass


if __name__ == "__main__":
    import pandas as pd
    from neo4j import GraphDatabase
    from tqdm import tqdm

    client = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"), database="discretemath")

    """
    // Neo4j 结构化查询
    MATCH p = (root)-[:RELATED*1..7]->(n)  // 限制路径深度在1到7层
        WHERE NOT ()-[:RELATED]->(root)  // root 是一级知识点
    WITH p, nodes(p) AS nodePath    // DFS 遍历
        UNWIND range(0, size(nodePath)-1) AS idx
    WITH nodePath[idx] AS currentNode, idx + 1 AS level,
        CASE 
            WHEN idx > 0 THEN nodePath[idx-1].name 
            ELSE null 
        END AS predecessor,
        CASE 
            WHEN idx < size(nodePath)-1 THEN nodePath[idx+1].name 
            ELSE null 
        END AS successor
    RETURN 
        CASE level WHEN 1 THEN currentNode.name END AS `一级知识点`,
        CASE level WHEN 2 THEN currentNode.name END AS `二级知识点`,
        CASE level WHEN 3 THEN currentNode.name END AS `三级知识点`,
        CASE level WHEN 4 THEN currentNode.name END AS `四级知识点`,
        CASE level WHEN 5 THEN currentNode.name END AS `五级知识点`,
        CASE level WHEN 6 THEN currentNode.name END AS `六级知识点`,
        CASE level WHEN 7 THEN currentNode.name END AS `七级知识点`,
        predecessor AS `前置知识点`,
        successor AS `后置知识点`
    LIMIT 50000
    """


    def remove_float(values: set):
        error_value = []
        for value in values:
            if isinstance(value, float):
                error_value.append(value)
        for value in error_value:
            values.remove(value)
        return values


    # 读取 CSV 文件
    df = pd.read_csv('export (11).csv')

    # 1 遍历一行
    unique_dict = {}
    for index, row in tqdm(df.iterrows()):
        unique_col = row.iloc[0:7]
        tup = tuple(unique_col.tolist())
        if tup not in unique_dict:
            set_7 = set()
            set_8 = set()
            set_7.add(row.iloc[7])
            set_8.add(row.iloc[8])
            unique_dict[tup] = (set_7, set_8)
        else:
            # merge
            old_set_7 = unique_dict[tup][0]
            old_set_8 = unique_dict[tup][1]
            old_set_7.add(row.iloc[7])
            old_set_8.add(row.iloc[8])
            unique_dict[tup] = (old_set_7, old_set_8)
    # 3 unique_dict transform to DataFrame
    new_df = pd.DataFrame(columns=df.columns.append(pd.Index(["cnt", "desc"])))
    for k, v in tqdm(unique_dict.items()):
        remove_float(v[0])
        remove_float(v[1])
        temp_desc = ""
        # find aim key
        aim_node1 = ""
        for i in range(7):
            if isinstance(k[i], str) and len(k[i]) > 0:
                aim_node1 = k[i]
        # get desc from database
        for aim_node2 in v[1]:
            temp_desc += client.execute_query(
                f"match (n1) where n1.name = '{aim_node1}' "
                f"match (n2) where n2.name = '{aim_node2}' "
                f"match (n1)-[r]->(n2) return r.description")[0][0][0]
            temp_desc += ";\n"
        temp_cnt = len(v[1])
        temp_df = pd.DataFrame([list(k) + [";".join(v[0]), ";".join(v[1]), temp_cnt, temp_desc]],
                               columns=new_df.columns)
        new_df = pd.concat([new_df, temp_df], ignore_index=True)
    # 保存去重合并后的数据
    new_df.to_csv('unique.csv', index=False)
    print('done')
