import asyncio
from typing import Callable

from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from graphmind.core.base import GraphmindModel


def task_chain(models: GraphmindModel) -> Runnable:
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ]
    )
    chain = prompt_template | models.llm | StrOutputParser()
    return chain


def task_batch(models: GraphmindModel,
               batch_lists: list[dict],
               enable_continue: bool = False,
               reduce_continue: Callable = None) -> list[str]:
    async def history_ainvoke(inputs: list[BaseMessage]):
        output = await _history_chain(models).ainvoke(inputs)
        if enable_continue:
            return await _task_continue_check(inputs, output, models, reduce_continue)
        return output

    async def run_batch(batch_lists: list[dict]):
        message_lists = [_dict_to_message(invokable) for invokable in batch_lists]
        task_batch_outputs = await asyncio.gather(*[history_ainvoke(message_list) for message_list in message_lists])
        return task_batch_outputs

    return asyncio.run(run_batch(batch_lists))


def _history_chain(models: GraphmindModel) -> Runnable:
    chain = models.llm | StrOutputParser()
    return chain


def _dict_to_message(invokable: dict) -> list[BaseMessage]:
    messages = []
    for key, value in invokable.items():
        if "system" in key:
            messages.append(SystemMessage(content=value))
        elif "human" in key or "user" in key:
            messages.append(HumanMessage(content=value))
        elif "ai" in key:
            messages.append(AIMessage(content=value))
    return messages


async def _task_continue_check(inputs: list[BaseMessage],
                               output: str,
                               models: GraphmindModel,
                               reduce_continue: Callable,
                               output_result: str = None) -> str | dict:
    """
    检查输出是否完整，如果不完整，在此处无限循环调用，直至任务完成
    Args:
        inputs: 第一轮任务的输入 & 前几轮任务的输入和输出
        output: 第一轮任务的输出 & 最新一轮任务的输出
        models: 模型集合
        reduce_continue: 多个模型输出的合并函数
        output_result: 用于存储最终合并结果的字典

    Returns:
        str: 最终合并的输出
    """
    if not output_result:
        output_result = output
    # 设置一个递归深度限制，以避免无限递归
    MAX_RECURSION_DEPTH = 8
    if "任务完成" in output or len(inputs) >= MAX_RECURSION_DEPTH:
        # 如果任务完成，返回最终合并的输出；要是第一轮任务就已经完成，返回第一轮任务的输出
        output_result.replace("任务完成", "")
        return output_result
    else:
        # 创建新的输入列表，而不是修改原始列表
        new_inputs = inputs + [
            AIMessage(content=output),
            HumanMessage(content="请继续。如果任务已经完成，请输入'任务完成'，否则继续按要求执行任务。")
        ]
        # 新一轮的输出
        new_output = await _history_chain(models).ainvoke(new_inputs)
        # 合并新输出和历史输出
        combined_output = reduce_continue(output_result, new_output)
        # 递归调用
        return await _task_continue_check(new_inputs, new_output, models, reduce_continue, combined_output)


__all__ = ["task_chain", "task_batch"]
