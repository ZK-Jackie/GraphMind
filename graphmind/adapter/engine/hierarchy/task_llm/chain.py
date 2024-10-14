import asyncio
import warnings
from typing import Callable

from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from graphmind.adapter.engine.hierarchy.reporter import GraphmindReporter
from graphmind.adapter.structure import BaseTask
from graphmind.core.base import GraphmindModel


def _chat_chain(models: GraphmindModel) -> Runnable:
    """
    根据已给 LLM 模型创建单轮聊天链，不建议用户在其他地方直接调用，调用时必须提供 `system_prompt` 和 `user_prompt` 键值对
    Args:
        models: Graphmind 模型合集

    Returns:
        LangChain `Runnable` 普通单轮 LLM 链
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ]
    )
    chain = prompt_template | models.llm | StrOutputParser()
    return chain


def chat_invoke(models: GraphmindModel,
                inputs: dict) -> str | None:
    """
    执行单轮任务
    Args:
        models: Graphmind 模型合集
        inputs: 输入提示词，必须包含 `system_prompt` 和 `user_prompt` 键值对

    Returns:
        str: 任务执行结果
    """

    async def ainvoke_chain():
        async with models.llm_semaphore:
            chain = _chat_chain(models)
            return await chain.ainvoke(inputs)

    def invoke_chain():
        return _chat_chain(models).invoke(inputs)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 如果事件循环已经在运行，使用 create_task 启动任务，并立即等待任务完成
        task = asyncio.create_task(ainvoke_chain())
        # 这里直接返回任务对象
        try:
            # 这里需要通过 await 直接获取任务的结果
            return loop.run_until_complete(task)
        except Exception as e:
            print(f"Error occurred: {e}")
            return ""
    else:
        # 如果没有事件循环在运行，直接使用同步调用
        try:
            return invoke_chain()
        except Exception as e:
            print(f"Error occurred: {e}")
            return ""


async def chat_ainvoke(models: GraphmindModel,
                       inputs: dict) -> str:
    """
    异步执行单轮任务
    Args:
        models: Graphmind 模型合集
        inputs: 输入提示词，必须包含 `system_prompt` 和 `user_prompt` 键值对

    Returns:
        str: 任务执行结果

    """
    async with models.llm_semaphore:
        chain = _chat_chain(models)
        return await chain.ainvoke(inputs)


def _chat_chain_custom_prompts(models: GraphmindModel) -> Runnable:
    """
    根据已给 LLM 模型创建对话任务链，不建议用户在其他地方直接调用，调用时必须提供消息数组
    Args:
        models:

    Returns:

    """
    chain = models.llm | StrOutputParser()
    return chain


def raw_chat_chain_invoke(models: GraphmindModel,
                          inputs: list[BaseMessage]) -> str:
    """
    执行 LangChain 消息对话任务
    Args:
        models: Graphmind 模型合集
        inputs: LangChain 消息数组

    Returns:
        str: 任务执行结果
    """

    async def ainvoke_chain():
        async with models.llm_semaphore:
            chain = _chat_chain_custom_prompts(models)
            return await chain.ainvoke(inputs)

    def invoke_chain():
        return _chat_chain_custom_prompts(models).invoke(inputs)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 如果事件循环已经在运行，使用 run_until_complete
        result = loop.run_until_complete(ainvoke_chain())
    else:
        # 否则，使用 asyncio.run()
        result = invoke_chain()
    return result


async def raw_chat_chain_ainvoke(models: GraphmindModel,
                                 inputs: list[BaseMessage]) -> str:
    """
    执行 LangChain 消息对话任务，异步
    Args:
        models: Graphmind 模型合集
        inputs: LangChain 消息数组

    Returns:

    """
    async with models.llm_semaphore:
        chain = _chat_chain_custom_prompts(models)
        return chain.invoke(inputs)


def chat_batch(models: GraphmindModel,
               batch_lists: list[dict],
               reporter: GraphmindReporter = None,
               enable_continue: bool = False,
               reduce_continue: Callable = None) -> list[str]:
    """
    批量执行 单轮 / 多轮任务，调用时 `batch_lists` 中的每个字典必须含 `system_prompt` 和 `user_prompt` 键值对

    Args:
        models: Graphmind 模型合集
        batch_lists: 提示词字典列表，每个字典包含 `system_prompt` 和 `user_prompt` 键值对
        reporter: 工作汇报器对象，得是**已经完成初始化的**对象
        enable_continue: 是否启用多轮任务
        reduce_continue: 多轮任务合并函数

    Returns:
        list[str]: 多任务执行结果列表

    Notes:
        附 `batch_lists` 格式:
            [{"system_prompt": task.task_system_prompt, "user_prompt": task.task_user_prompt},
             {"system_prompt": task.task_system_prompt, "user_prompt": task.task_user_prompt},
             ...
            ]
    """

    async def continuously_invoke(inputs: list[BaseMessage]):
        try:
            batch_item_output = await raw_chat_chain_ainvoke(models, inputs)  # 异步提速
            if enable_continue:
                batch_item_output = await _chat_continue_check(inputs, batch_item_output, models, reduce_continue)
        except Exception as e:
            print(f"Error occurred: {e}")
            batch_item_output = ""
        if reporter:
            reporter.update(1)
        return batch_item_output

    async def run_batch_invoke(now_batch_list: list[list[BaseMessage]]) -> list[str]:
        batch_tasks = [asyncio.create_task(continuously_invoke(batch_item)) for batch_item in now_batch_list]
        now_batch_output = await asyncio.gather(*batch_tasks)
        return now_batch_output

    async def run_batch(run_batch_lists: list[dict]):
        message_lists = [_dict_to_message(invokable) for invokable in run_batch_lists]
        batch_outputs = []
        for i in range(0, len(message_lists), models.task_buffer_size):
            batch_buffer = message_lists[i:i + models.task_buffer_size]  # 取一批任务
            batch_outputs += await run_batch_invoke(batch_buffer)  # 执行一批任务
        return batch_outputs

    return asyncio.run(run_batch(batch_lists))


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


async def _chat_continue_check(inputs: list[BaseMessage],
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
        # 创建新输入列表，而不是修改原始列表
        new_inputs = inputs + [
            AIMessage(content=output),
            HumanMessage(content="请继续。如果任务已经完成，请输入'任务完成'，否则继续按要求执行任务。")
        ]
        # 新一轮的输出
        new_output = await raw_chat_chain_ainvoke(models, new_inputs)
        # 合并新输出和历史输出
        combined_output = reduce_continue(output_result, new_output)
        # 递归调用
        return await _chat_continue_check(new_inputs, new_output, models, reduce_continue, combined_output)


def task_invoke(models: GraphmindModel,
                task: BaseTask,
                reporter: GraphmindReporter = None,
                enable_continue: bool = False,
                reduce_continue: Callable = None) -> None:
    """
    执行任务，仅支持单个任务，会阻塞
    Args:
        models: Graphmind 模型合集
        task: 任务对象
        reporter: 工作汇报器对象，得是**已经完成初始化的**对象
        enable_continue: 是否启用多轮任务
        reduce_continue: 多轮任务合并函数

    Returns:
        None
    """
    if enable_continue:
        warnings.warn(f"暂不支持多轮对话任务！请等待后续版本！将返回单轮对话结果！{reduce_continue}")
    task.task_output = chat_invoke(models,
                                   {"system_prompt": task.task_system_prompt,
                                    "user_prompt": task.task_user_prompt})
    if reporter:
        reporter.update(1)


def task_batch(models: GraphmindModel,
               tasks: list[BaseTask],
               reporter: GraphmindReporter = None,
               enable_continue: bool = False,
               reduce_continue: Callable = None) -> None:
    """
    执行任务列表，会阻塞
    Args:
        models: Graphmind 模型合集
        tasks: 任务列表
        reporter: 工作汇报器对象，得是**已经完成初始化的**对象
        enable_continue: 是否启用多轮任务
        reduce_continue: 多轮任务合并函数

    Returns:
        None
    """
    temp_sys_usr_prompts = [{"system_prompt": task.task_system_prompt, "user_prompt": task.task_user_prompt}
                            for task in tasks]
    task_batch_outputs = chat_batch(models,
                                    temp_sys_usr_prompts,
                                    reporter,
                                    enable_continue,
                                    reduce_continue)
    for task, output in zip(tasks, task_batch_outputs):
        output.replace("任务完成", "")
        task.task_output = output
        task.task_status = "PROCESSED"


async def task_ainvoke(models: GraphmindModel,
                       task: BaseTask,
                       reporter: GraphmindReporter = None,
                       enable_continue: bool = False,
                       reduce_continue: Callable = None) -> None:
    """
    异步执行任务，仅支持单个任务
    Args:
        models: Graphmind 模型合集
        task: 任务对象
        reporter: 工作汇报器对象，得是**已经完成初始化的**对象
        enable_continue: 是否启用多轮任务
        reduce_continue: 多轮任务合并函数

    Returns:
        None
    """
    if enable_continue:
        warnings.warn(f"暂不支持多轮对话任务！请等待后续版本！将返回单轮对话结果！{reduce_continue}")
    temp_output = await chat_ainvoke(
        models,
        {"system_prompt": task.task_system_prompt,
         "user_prompt": task.task_user_prompt}
    )
    task.task_output = temp_output
    if reporter:
        reporter.update(1)
    return


async def task_abatch(models: GraphmindModel,
                      tasks: list[BaseTask],
                      reporter: GraphmindReporter = None,
                      enable_continue: bool = False,
                      reduce_continue: Callable = None) -> None:
    """
    异步执行任务列表
    Args:
        models: Graphmind 模型合集
        tasks: 任务列表
        reporter: 工作汇报器对象，得是**已经完成初始化的**对象
        enable_continue: 是否启用多轮任务
        reduce_continue: 多轮任务合并函数

    Returns:
        None
    """
    temp_sys_usr_prompts = [{"system_prompt": task.task_system_prompt,
                             "user_prompt": task.task_user_prompt}
                            for task in tasks]

    async def continuously_invoke(inputs: list[BaseMessage]):
        abatch_invoke_output = await raw_chat_chain_ainvoke(models, inputs)  # 异步提速
        if enable_continue:
            abatch_invoke_output = await _chat_continue_check(inputs,
                                                              abatch_invoke_output,
                                                              models,
                                                              reduce_continue)
        if reporter:
            reporter.update(1)
        return abatch_invoke_output

    async def run_abatch_invoke(now_batch_list: list[list[BaseMessage]]) -> list[str]:
        abatch_tasks = [asyncio.create_task(continuously_invoke(now_batch)) for now_batch in now_batch_list]
        now_batch_output = await asyncio.gather(*abatch_tasks)
        return now_batch_output

    async def run_abatch(run_batch_lists: list[dict]):
        message_lists = [_dict_to_message(invokable) for invokable in run_batch_lists]
        batch_outputs = []
        for i in range(0, len(message_lists), models.task_buffer_size):
            batch_buffer = message_lists[i:i + models.task_buffer_size]  # 取一批任务
            batch_outputs += await run_abatch_invoke(batch_buffer)  # 执行一批任务
        return batch_outputs

    task_batch_outputs = await run_abatch(temp_sys_usr_prompts)

    for task, output in zip(tasks, task_batch_outputs):
        output.replace("任务完成", "")
        task.task_output = output
        task.task_status = "PROCESSED"
    return


__all__ = ["task_invoke", "task_batch", "task_ainvoke", "task_abatch"]
