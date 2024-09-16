from graphmind.adapter.engine.base import BaseEntity, BaseRelation

"""
    {
      "[实体1名称]": {
        "实体类型": "[实体类型]",
        "[属性名1]": "[属性值1]",
        "[属性名2]": "[属性值2]",
        ...
      },
      "[实体2名称]": {
        "实体类型": "[实体类型]",
        "[属性名1]": "[属性值1]",
        ...
      },
      ...
    }
"""
def entity_extract_parser(llm_outputs: dict | list[dict]) -> list:
    """
    将 json 字符串转换为对象列表
    """
    entity_list = []
    try:
        for entity_name, entity_attr in llm_outputs.items():
            entity_list.append(_parse_entity(entity_name, entity_attr))
    except:
        raise UserWarning(f"Failed to parse to json `{llm_outputs}` into entity list")
    return entity_list


def _parse_entity(name, attr) -> BaseEntity:
    return BaseEntity(
        name=name,
        type=attr.get("实体类型", None) or attr.get("实体类型", None),
        attributes=attr
    )


"""
  [
    {
      "entity1": "实体名称",
      "entity2": "实体名称",
      "relation": "关系词汇",
      "summary": "关系总结"
    },
    ...
  ]
"""
def relation_extract_parser(llm_outputs: dict | list[dict]) -> list:
    """
    将 json 字符串转换为对象列表
    """
    relation_list = []
    try:
        if isinstance(llm_outputs, list):
            for llm_output in llm_outputs:
                relation_list.append(_build_relation(llm_output))
        elif isinstance(llm_outputs, dict):
            relation_list.append(_build_relation(llm_outputs))
    except:
        raise UserWarning(f"Failed to parse to json `{llm_outputs}` into relation list")
    return relation_list


def _build_relation(output: dict) -> BaseRelation:
    return BaseRelation(
        start=output.get("entity1", None) or output.get("实体1", None),
        end=output.get("entity2", None) or output.get("实体2", None),
        relation=output.get("relation", None) or output.get("关系", None),
        description=output.get("summary", None) or output.get("总结", None),
        source=output.get("source", None)
    )


"""
    {
      "名称": "[实体名称]",
      "属性": {
        "[属性1]": "[属性值1]",
        "[属性2]": "[属性值2]",
        ...
      }
    }
"""
def entity_merge_parser(llm_output: dict) -> dict:
    """
    处理合并结果
    """
    new_attr = {}
    try:
        new_attr = llm_output["属性"]
    except:
        raise UserWarning(f"Failed to parse to json `{llm_output}` into entity attributes")
    return new_attr

