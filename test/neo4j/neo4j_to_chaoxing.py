import pandas as pd
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"
NEO4J_DATABASE = "discrete-math-flash"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD), database=NEO4J_DATABASE)

chaoxing_df = pd.DataFrame(
    columns=["一级知识点", "二级知识点", "三级知识点", "四级知识点", "五级知识点", "六级知识点", "七级知识点",
             "前置知识点", "后置知识点", "关联知识点", "知识点说明"])


def level_query(df, level):
    with driver.session() as session:
        result = session.run("MATCH (n) WHERE n.level = $level RETURN n", level=str(level))
        for record in result:
            desc = ""
            for key, value in record["n"].items():
                if key not in ["name", "uid", "level", "source"]:
                    desc += f"{key}: {value}\n" + "；"
            desc = desc[:-1]
            # 所有单斜杠替换为双斜杠

            new_df = pd.DataFrame(
                columns=["一级知识点", "二级知识点", "三级知识点", "四级知识点", "五级知识点", "六级知识点",
                         "七级知识点",
                         "前置知识点", "后置知识点", "关联知识点", "知识点说明"])
            new_df.loc[0] = [None] * 11
            new_df.iloc[0, level - 1] = record["n"]["name"]
            new_df.iloc[0, 10] = desc
            df = pd.concat([df, new_df], ignore_index=True)
    return df


last_end_index = 0


def link_query(df, level):
    global last_end_index
    # 逐行遍历df
    for i in range(last_end_index, df.shape[0]):
        aim_start = df.iloc[i, level - 1]
        if aim_start is None:
            last_end_index = i
            break
        with driver.session() as session:
            result = session.run("MATCH (n)-[]->(m) WHERE n.name = $name RETURN m.level, m.name", name=aim_start)
            front_list = []
            back_list = []
            link_list = []
            for record in result:
                if int(record["m.level"]) == level:
                    link_list.append(record["m.name"])
                elif int(record["m.level"]) > level:
                    back_list.append(record["m.name"])
                else:
                    front_list.append(record["m.name"])
            df.iloc[i, 7] = ";".join(front_list)
            df.iloc[i, 8] = ";".join(back_list)
            df.iloc[i, 9] = ";".join(link_list)
    return df


for i in range(1, 6):
    chaoxing_df = level_query(chaoxing_df, i)
for i in range(1, 6):
    chaoxing_df = link_query(chaoxing_df, i)

chaoxing_df.to_csv("chaoxing.csv", index=False)
