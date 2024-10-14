# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Utility functions for the OpenAI API."""

import json
import logging
import re
import ast
from typing import Literal

from json_repair import repair_json

log = logging.getLogger(__name__)


def try_parse_ast_to_json(function_string: str) -> tuple[str, dict]:
    """
     # 示例函数字符串
    function_string = "tool_call(first_int={'title': 'First Int', 'type': 'integer'}, second_int={'title': 'Second Int', 'type': 'integer'})"
    :return:
    """

    tree = ast.parse(str(function_string).strip())
    ast_info = ""
    json_result = {}
    # 查找函数调用节点并提取信息
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            function_name = node.func.id
            args = {kw.arg: kw.value for kw in node.keywords}
            ast_info += f"Function Name: {function_name}\r\n"
            for arg, value in args.items():
                ast_info += f"Argument Name: {arg}\n"
                ast_info += f"Argument Value: {ast.dump(value)}\n"
                json_result[arg] = ast.literal_eval(value)

    return ast_info, json_result


def try_parse_json_object(input_str: str,
                          expect_type: Literal["dict", "list"] = "dict"
                          ) -> tuple[str, dict] | tuple[str, list]:
    """JSON cleaning and formatting utilities."""
    # Sometimes, the LLM returns a json string with some extra description, this function will clean it up.
    # 使用正则表达式找到需要转义的反斜杠
    input_str = re.sub(r'(?<!\\)\\(?!["\\/n])', r'\\\\', input_str)
    #  first try
    result = None
    try:
        # Try parse first
        result = json.loads(input_str)
    except json.JSONDecodeError:
        log.info("Warning: Error decoding faulty json - 1/5")
    if result:
        return input_str, result

    # second try
    try:
        result = json.loads(input_str.split("```")[1])
    except Exception as e:
        log.info("Warning: Error decoding faulty json - 2/5 - %s", e)
    if result:
        return input_str, result

    # third try
    try:
        result = _extract_json_code_block(input_str)
    except Exception as e:
        print(e)
        log.info("Warning: Error decoding faulty json - 3/5 - %s", e)
    if result:
        return json.dumps(result, ensure_ascii=False), result

    # forth try
    if expect_type == "list":
        try:
            pattern = re.compile(r'\[(.*?)\]', re.DOTALL)
            matches = pattern.findall(input_str)
            result = json.loads(matches[0])
        except Exception as e:
            log.info("Warning: Error decoding faulty json - 4/5 - %s", e)
        if result:
            return json.dumps(result, ensure_ascii=False), result

    # fifth try
    if expect_type == "list":
        pattern = re.compile(r'\{.*?\}', re.DOTALL)
        matches = pattern.findall(input_str)
        try:
            dict_objects = []
            for match in matches:
                try:
                    # 尝试将匹配的内容解析为字典对象
                    dict_obj = json.loads(match)
                    if isinstance(dict_obj, dict):
                        dict_objects.append(dict_obj)
                except Exception:
                    continue
            result = dict_objects
        except Exception as e:
            log.info("Warning: Error decoding faulty json, attempting repair - 5/5 - %s", e)
        if result:
            return json.dumps(result, ensure_ascii=False), result

    # repair json
    _pattern = r"\{(.*)\}"
    _match = re.search(_pattern, input_str)
    input_str = "{" + _match.group(1) + "}" if _match else input_str

    # Clean up json string.
    input_str = (
        input_str.replace("{{", "{")
        .replace("}}", "}")
        .replace('"[{', "[{")
        .replace('}]"', "}]")
        .replace("\\", " ")
        .replace("\\n", " ")
        .replace("\n", " ")
        .replace("\r", "")
        .strip()
    )

    # Remove JSON Markdown Frame
    if input_str.startswith("```"):
        input_str = input_str[len("```"):]
    if input_str.startswith("```json"):
        input_str = input_str[len("```json"):]
    if input_str.endswith("```"):
        input_str = input_str[: len(input_str) - len("```")]

    try:
        result = json.loads(input_str)
    except json.JSONDecodeError:
        # Fixup potentially malformed json string using json_repair.
        json_info = str(repair_json(json_str=input_str, return_objects=False, ensure_ascii=False))

        # Generate JSON-string output using best-attempt prompting & parsing techniques.
        try:

            if len(json_info) < len(input_str):
                json_info, result = try_parse_ast_to_json(input_str)
            else:
                result = json.loads(json_info)

        except json.JSONDecodeError:
            log.exception("error loading json, json=%s", input_str)
            raise json.JSONDecodeError
        else:
            if not isinstance(result, dict):
                log.exception("not expected dict type. type=%s:", type(result))
                raise json.JSONDecodeError
            return json_info, result
    else:
        return input_str, result


def _extract_json_code_block(raw_str: str):
    # Regular expression to match ```json ... ```
    pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
    # Find all matches
    matches = pattern.findall(raw_str)
    return json.loads(matches[0])
