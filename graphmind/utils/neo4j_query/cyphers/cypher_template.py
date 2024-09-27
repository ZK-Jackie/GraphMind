import asyncio
import json

from graphmind.adapter.database import GraphNeo4j
from graphmind.utils.dict_list_remove_dup import dict_list_remove_dup
from graphmind.utils.neo4j_query.base import CypherResult, RelatedNode

IGNORE_ATTRIBUTE = ['name', 'description', 'nameEmbeddings', 'description_embedding', "id", "human_readable_id", "uid"]


class EntityEnsureTemplate:
    name_fulltext_index_template = """
        CALL db.index.fulltext.queryNodes(\"nodeNameFulltextIndex\", \"{keyword}\") YIELD node, score
        WITH node, score
        ORDER BY score DESC
        LIMIT 10
        RETURN node, score
    """

    name_embeddings_index_template = """
        CALL db.index.vector.queryNodes('nodeNameVectorIndex', 5, {main_entity_embeddings}) YIELD node, score
        WITH node, score
        ORDER BY score DESC
        LIMIT 1
        RETURN node.name, node.description, score
    """

    @staticmethod
    def build_fulltext(keywords: str | list[str]) -> list[str]:
        if isinstance(keywords, str):
            keywords = [keywords]
        return [EntityEnsureTemplate.name_fulltext_index_template.format(keyword=keyword) for keyword in keywords]


class SingleNodeTemplate:
    single_node_template = """
        MATCH (n {{name: "{keyword}"}})
        RETURN n
    """

    @staticmethod
    def build_singlenode_queries(keywords: str | list[str]) -> list[str]:
        if isinstance(keywords, str):
            keywords = [keywords]
        return [SingleNodeTemplate.single_node_template.format(keyword=keyword) for keyword in keywords]

    @staticmethod
    def cypher_result_parser(query_results: list[dict]) -> list[CypherResult]:
        ret = []
        if len(query_results) == 0:
            return []
        for result in query_results:
            ret.append(CypherResult(node_name=result['n'].get('name', None),
                                    node_description=result['n'].get('description', None),
                                    node_attr={k: v for k, v in result['n'].items() if
                                               k not in IGNORE_ATTRIBUTE}))
        return ret

    @staticmethod
    def get_result_prompt(cypher_result: CypherResult) -> str:
        if not cypher_result:
            return "未找到相关信息"
        return cypher_result.rag_json_dict()

    @staticmethod
    def run_cypher_query(database: GraphNeo4j, entity_list: list[str]) -> str:
        # 1 构造查询
        cypher_queries = SingleNodeTemplate.build_singlenode_queries(entity_list)
        # 2 执行查询
        raw_result_list = asyncio.run(database.batch(cypher_queries))
        # 3 结果解析
        result_list = []
        for i in range(len(raw_result_list)):
            result_list.extend(SingleNodeTemplate.cypher_result_parser(raw_result_list[i]))
        # 4 构造结果prompt
        result_json = []
        for result in result_list:
            result_json.append(SingleNodeTemplate.get_result_prompt(result))
        return json.dumps({"nodes": result_json},
                          ensure_ascii=False, indent=2)


class MultiNodeTemplate:
    relationship_path_template = """
        MATCH p = ALL SHORTEST (n1 {{name: "{keyword1}"}})-[*..5]-(n2 {{name: "{keyword2}"}})
        RETURN [n in nodes(p)] AS nodeList, [r in relationships(p) | r.description] AS relationList
    """

    @staticmethod
    def build_multinode_queries(keywords: str | list[str]) -> list[str]:
        if isinstance(keywords, str):
            keywords = [keywords]
        ret = []
        # 握手问题
        for i in range(len(keywords)):
            for j in range(i + 1, len(keywords)):
                ret.append(
                    MultiNodeTemplate.relationship_path_template.format(keyword1=keywords[i], keyword2=keywords[j]))
        return ret

    @staticmethod
    def cypher_result_parser(query_results: list[dict]) -> list[CypherResult] | None:
        if len(query_results) == 0:
            return None
        batch_related_nodes = []
        for path in query_results:
            now_path_nodes = path['nodeList']
            now_path_relations = path['relationList']
            now_path_related_nodes = []
            for i in range(len(now_path_nodes)):
                now_path_related_nodes.append(CypherResult(node_name=now_path_nodes[i].get('name', None),
                                                  name_embedding=now_path_nodes[i].get('nameEmbeddings', None),
                                                  node_description=now_path_nodes[i].get('description', None),
                                                  description_embedding=now_path_nodes[i].get('description_embedding',
                                                                                              None),
                                                  node_attr={k: v for k, v in now_path_nodes[i].items() if
                                                             k not in IGNORE_ATTRIBUTE}))
            for i in range(len(now_path_relations)):
                relation = RelatedNode(related_name=None,  # 待我想想办法优化查询语句
                                       related_description=now_path_relations[i],
                                       previous_cypher_result=(
                                           now_path_related_nodes[i] if 0 <= i < len(now_path_nodes) else None
                                       ),
                                       next_cypher_result=(
                                           now_path_related_nodes[i + 1] if i < len(now_path_nodes) - 1 else None))
                now_path_related_nodes[i].related_nodes.append(relation)
            batch_related_nodes.append(now_path_related_nodes[0])
        return batch_related_nodes

    @staticmethod
    def get_result_prompt(cypher_results: list[CypherResult]) -> str:
        if not cypher_results:
            return "未找到相关信息"
        node_list = []
        relation_list = []
        # 遍历多链表
        for cypher_result in cypher_results:
            now_node = cypher_result
            while now_node:
                node_list.append(now_node.rag_json_dict())
                for relation in now_node.related_nodes:
                    relation_list.append(relation.rag_json_dict())
                if len(now_node.related_nodes) == 0:
                    break
                now_node = now_node.related_nodes[0].next_cypher_result
        # 字典列表去重
        node_list = dict_list_remove_dup(node_list, "node_name")
        relation_list = dict_list_remove_dup(relation_list, "relation_description")
        return json.dumps({"nodes": node_list, "relations": relation_list},
                          ensure_ascii=False, indent=2)

    @staticmethod
    def run_cypher_query(database: GraphNeo4j, entity_list: list[str]) -> str:
        # 1 构造查询
        cypher_queries = MultiNodeTemplate.build_multinode_queries(entity_list)
        # 2 执行查询
        raw_result_list = asyncio.run(database.batch(cypher_queries))
        # 3 结果解析
        result_list = []
        for i in range(len(raw_result_list)):
            # 对于每一句cypher查出的结果进行转化
            result_list.extend(MultiNodeTemplate.cypher_result_parser(raw_result_list[i]))
        # 4 构造结果prompt
        return MultiNodeTemplate.get_result_prompt(result_list)


class OverallNodeTemplate:
    all_links_template = """
        MATCH (n1)-[r]-(n2)
            WHERE n1.name = "{keyword}"
        RETURN n1, {{name: type(r), description: r.description}} AS r, n2
    """

    @staticmethod
    def build_overall_queries(keywords: str | list[str]) -> list[str]:
        if isinstance(keywords, str):
            keywords = [keywords]
        return [OverallNodeTemplate.all_links_template.format(keyword=keyword) for keyword in keywords]

    @staticmethod
    def cypher_result_parser(query_results: list[dict]) -> CypherResult | None:
        if len(query_results) == 0:
            return None
        related_nodes = []
        for couple in query_results:
            now_match_obj = couple['n2']
            now_relation_obj = couple['r']
            if len(related_nodes) == 0:
                # 第一个节点为中心节点
                now_origin_obj = couple['n1']
                related_nodes.append(CypherResult(node_name=now_origin_obj.get('name', None),
                                                  name_embedding=now_origin_obj.get('nameEmbeddings', None),
                                                  node_description=now_origin_obj.get('description', None),
                                                  description_embedding=now_origin_obj.get('description_embedding',
                                                                                           None),
                                                  node_attr={k: v for k, v in now_origin_obj.items() if
                                                             k not in IGNORE_ATTRIBUTE}))
            related_nodes.append(CypherResult(node_name=now_match_obj.get('name', None),
                                              name_embedding=now_match_obj.get('nameEmbeddings', None),
                                              node_description=now_match_obj.get('description', None),
                                              description_embedding=now_match_obj.get('description_embedding', None),
                                              node_attr={k: v for k, v in now_match_obj.items() if
                                                         k not in IGNORE_ATTRIBUTE}))
            relation = RelatedNode(related_name=None,  # 待我想想办法优化查询语句来解决这个None
                                   related_description=now_relation_obj.get('description', None),
                                   previous_cypher_result=related_nodes[-2],
                                   next_cypher_result=related_nodes[-1])
            related_nodes[0].related_nodes.append(relation)

        return related_nodes[0]

    @staticmethod
    def get_result_prompt(cypher_result: CypherResult) -> str:
        if not cypher_result:
            return "未找到相关信息"
        node_list = []
        relation_list = []
        # 遍历结点关联列表
        node_list.append(cypher_result.rag_json_dict())
        for relation in cypher_result.related_nodes:
            relation_list.append(relation.rag_json_dict())
            node_list.append(relation.next_cypher_result.rag_json_dict())
        return json.dumps({"nodes": node_list, "relations": relation_list},
                          ensure_ascii=False, indent=2)

    @staticmethod
    def run_cypher_query(database: GraphNeo4j, entity_list: list[str]) -> str:
        # 1 构造查询
        cypher_queries = OverallNodeTemplate.build_overall_queries(entity_list)
        # 2 执行查询 有一种狗血结果是查询结果为空 此时要注意返回 None
        raw_result_list = asyncio.run(database.batch(cypher_queries))
        if raw_result_list is None or raw_result_list[0] is None or len(raw_result_list) == 0:
            return "None"
        # 3 结果解析
        result_list = []
        for i in range(len(raw_result_list)):
            result_list.append(OverallNodeTemplate.cypher_result_parser(raw_result_list[i]))
        # 4 构造结果prompt
        result_json = []
        for result in result_list:
            result_json.append(result.rag_json_dict())
        return OverallNodeTemplate.get_result_prompt(result_list[0])
