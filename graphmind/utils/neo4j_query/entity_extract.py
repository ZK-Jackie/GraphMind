import asyncio
import json
import re
from typing import List

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseGenerationOutputParser
from langchain_core.outputs import ChatGeneration, Generation
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from graphmind.utils.neo4j_query.prompts import entity as prompts
from graphmind.adapter.database import GraphNeo4j
from graphmind.utils.neo4j_query.cypher_query import CypherResult
from graphmind.utils.neo4j_query.cyphers.cypher_template import EntityEnsureTemplate

QUERY_TYPE = ["single", "multi", "overall"]


class EntityCandidate:
    cypher_candidate: CypherResult | None = None
    score: float | None = None

    def __init__(self, cypher_candidate=None, score=None):
        self.cypher_candidate = cypher_candidate
        self.score = score

    def __str__(self):
        return self.cypher_candidate.node_name

    def __lt__(self, other):
        return self.score < other.score


class EntityExtractResult:
    entity: str | list[str] | None = None
    candidate: list[EntityCandidate] | None = None
    final_entity: str | list[str] | None = None

    def __init__(self, entity=None, candidate=None, final_entity=None):
        self.entity = entity
        self.candidate = candidate
        self.final_entity = final_entity


async def entity_extract(llm: ChatOpenAI,
                         embeddings: OpenAIEmbeddings,
                         database: GraphNeo4j,
                         query_chunk: str,
                         strategy: str | int = 'top_n') -> list[EntityExtractResult]:
    """
    实体提取。
    Args:
        llm(ChatOpenAI): 用于实体提取的语言模型
        embeddings(OpenAIEmbeddings): 用于实体比较的语言模型（可能没用）
        database(GraphNeo4j): 数据库连接
        query_chunk(str): 用户查询语句的子问题句
        strategy(str): 实体确定策略，top_n/llm；提供数字时，表示采用 top_n 策略并设定 n 值。当前仅支持 top_1 策略

    Returns:
        list[EntityExtractResult]: 实体提取结果列表
    """
    # 1 实体列举
    result_list = entity_llm_extract(llm, query_chunk)
    # 2 数据库逐一检索，实体确定
    await entity_database_query(database, result_list)
    # 3 候选判定（top_n/llm）
    if strategy == 'top_n':
        # 3.1 top_n
        for result in result_list:
            result.final_entity = result.candidate[0].cypher_candidate.node_name
    elif strategy == 'llm':
        # 3.2 llm
        await entity_llm_decide(llm, result_list, query_chunk)
    return result_list


def entity_llm_extract(llm: ChatOpenAI,
                       query_chunk: str) -> list[EntityExtractResult] | None:
    """
    步骤一：使用 LLM 提取实体。
    Args:
        llm(ChatOpenAI): 执行实体提取的 LLM
        query_chunk(str): 用户查询语句的子问题句

    Returns:
        list[EntityExtractResult]: 初步进行实体提取结果列表
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompts.system_prompt),
            ("user", prompts.user_prompt_template),
        ]
    )
    parser = EntityResultParser()
    chain = prompt | llm | parser
    obj: list[EntityExtractResult] = chain.invoke({"input": query_chunk})
    return obj


async def entity_database_query(database: GraphNeo4j,
                                result_obj: list[EntityExtractResult]) -> list[EntityExtractResult] | None:
    """
    步骤二：使用数据库查询确定实体。
    Args:
        database(GraphNeo4j): 数据库连接
        result_obj(EntityExtractResult): 实体提取结果对象

    Returns:
        EntityExtractResult: 实体提取结果对象
    """

    async def query_entity(entity_result: EntityExtractResult) -> None:
        """
        查询实体，用于填充实体结果中的 EntityCandidate。
        Args:
            entity_result(EntityExtractResult): 实体结果对象

        Returns:
            None
        """
        if hasattr(entity_result, '_processed') and entity_result._processed:
            return
        # 构造查询语句
        entity = entity_result.entity
        cypher = EntityEnsureTemplate.build_fulltext(entity)[0]
        # 执行查询
        result = database.query(cypher)
        # 整理 candidate 结果
        temp_candidate = []
        for record in result:
            temp_node = record.get("node")
            temp_cypher = CypherResult(
                cypher=cypher,
                node_name=temp_node.get("name"),
                node_description=temp_node.get("description"),
                node_attr={k: v for k, v in temp_node.items() if k not in ["name", "description"]}
                # 去除name和description以外的属性
            )
            temp_candidate.append(
                EntityCandidate(cypher_candidate=temp_cypher, score=record.get("score"))
            )
        # 保存入实体结果对象
        entity_result.candidate = temp_candidate
        entity_result._processed = True

    # 针对每个节点都进行异步查询
    tasks = [query_entity(obj) for obj in result_obj]
    await asyncio.gather(*tasks)
    return result_obj


async def entity_top_decide(n: int,
                            result_obj: list[EntityExtractResult]) -> list[EntityExtractResult] | None:
    """
    使用 top_n 策略确定实体。（TODO）
    Args:
        n(int): top_n 策略中的 n 值
        result_obj(list[EntityExtractResult]): 实体提取结果对象

    Returns:
        list[EntityExtractResult]: 实体提取结果对象

    """
    pass


async def entity_llm_decide(llm: ChatOpenAI,
                            result_obj: list[EntityExtractResult],
                            user_query: str) -> list[EntityExtractResult] | None:
    """
    步骤三：使用 LLM 确定实体。（TODO）
    Args:
        llm:
        result_obj:
        user_query:

    Returns:

    """
    pass


class EntityResultParser(BaseGenerationOutputParser[str]):
    """
    自定义的 Langchain 输出解析器，用于解析实体提取的结果。
    """

    def _extract_dict(self, raw_str: str):
        exceptions = []
        # 1 尝试直接解析json字符串
        try:
            return json.loads(raw_str)
        except Exception as e1:
            exceptions.append(e1)
        # 2 尝试从代码块中提取json字符串
        try:
            return json.loads(raw_str.split("```")[1])
        except Exception as e2:
            exceptions.append(e2)
        # 3 尝试自定义的提取方法
        try:
            return self.__extract_json_code_block(raw_str)
        except Exception as e3:
            exceptions.append(e3)
        # 如果所有尝试都失败了，抛出UserWarning
        raise OutputParserException(f"Failed to parse to json: {raw_str}") from exceptions[0] if exceptions else None

    @staticmethod
    def __extract_json_code_block(raw_str: str) -> dict:
        # 匹配所有代码块：```json ... ```
        pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
        # 提取 json 字符串
        matches = pattern.findall(raw_str)
        # 返回第一个匹配的 json 字符串
        return json.loads(matches[0])

    def parse_result(self, result: List[Generation], *, partial: bool = False) -> list[EntityExtractResult]:
        # Validate Generation
        if len(result) != 1:
            # 该输出解析器只能用于单一结果生成模型生成的内容
            raise NotImplementedError(
                "This output parser can only be used with a single generation."
            )
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            # 该输出解析器只能用于聊天生成
            raise OutputParserException(
                "This output parser can only be used with a chat generation."
            )
        # 使用自定义解析法
        result_dict = self._extract_dict(generation.message.content)
        # 生成返回对象
        result_entity_list = result_dict.get("实体", [])
        ret_list = []
        for result_entity in result_entity_list:
            entity = EntityExtractResult(
                entity=result_entity
            )
            ret_list.append(entity)
        return ret_list
