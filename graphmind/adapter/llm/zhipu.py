import os
import re
import warnings
from typing import List, Any, Coroutine
import json
import asyncio
from pydantic import model_validator, Field
from tqdm import tqdm

from zhipuai import ZhipuAI

from graphmind.adapter.structure.base import BaseTask
from graphmind.adapter.llm.base import BaseTaskLLM, BaseTextEmbeddings


####################################################################################################
# Task Model
####################################################################################################
class TaskZhipuAI(BaseTaskLLM):
    json_output: bool = Field(description="Whether to parse the output to json", default=False)

    _zhipu_client: ZhipuAI | None = None
    _progress_bar: tqdm | None = None

    _retry_tasks: List[BaseTask] = []
    _resume_tasks: List[BaseTask] = []

    @model_validator(mode="after")
    def create_zhipu_client(self):
        self._zhipu_client = ZhipuAI(api_key=self.api_key)
        return self

    def execute_task(self,
                     task: BaseTask | List[BaseTask],
                     mode="async",
                     **kwargs) -> Coroutine[Any, Any, BaseTask | list[BaseTask]] | BaseTask | tuple[Any]:
        # 2 进度条
        # TODO 换成装饰器围绕递增的进度条
        self._progress_bar = kwargs.get("progress_bar")
        # 3 执行任务
        if mode == "sync":
            return self._sync_execute(task, **kwargs)
        elif mode == "async":
            return asyncio.run(self._async_execute(task, **kwargs))

    def _sync_submit_single(self, task: BaseTask, **kwargs) -> BaseTask:
        # 1 发出请求
        client = self._zhipu_client
        response = client.chat.completions.create(
            model=self.llm_name,
            messages=[
                {"role": "system", "content": task.task_system_prompt},
                {"role": "user", "content": task.task_user_prompt},
            ],
            temperature=kwargs.get("temperature") or self.llm_kwargs.get("temperature") or 0.1,
        )
        # 2 获取结果
        task.task_output = response.choices[0].message.content  # 文本结果
        # TODO multi-round 情况下的处理，async同理
        if response.choices[0].finish_reason in ["network_error"]:
            # 记录晚点要重试或继续的任务
            self._retry_tasks.append(task)
        elif response.choices[0].finish_reason in ["max_tokens", "length"]:
            # 记录晚点要继续的任务
            self._resume_tasks.append(task)
        # 3 结果解析
        try:
            task.task_result = _llm_output_parser(task.task_output, engine_json_output=self.json_output, **kwargs)
            task.task_status = "SUCCESS"
        except UserWarning:
            warnings.warn(f"Failed to parse : {task.task_output}")
            task.task_status = "PARSING_FAILED"
            task.task_result = {"output": task.task_output, "result": task.task_result}
        # 进度条递增
        if self._progress_bar:
            self._progress_bar.update(1)
        return task

    def _sync_execute(self, task: BaseTask | List[BaseTask], **kwargs) -> BaseTask | List[BaseTask]:
        if isinstance(task, BaseTask):
            return self._sync_submit_single(task, **kwargs)
        elif isinstance(task, List):
            for task in task:
                self._sync_submit_single(task, **kwargs)
            return task

    async def _async_submit_single(self, task: BaseTask, **kwargs):
        # 准备请求对象和信息
        client = self._zhipu_client
        task_messages = [
            {"role": "system", "content": task.task_system_prompt},
            {"role": "user", "content": task.task_user_prompt},
        ]
        # 异步、任务式请求
        response = client.chat.asyncCompletions.create(
            model=self.llm_name,
            messages=task_messages,
            temperature=kwargs.get("temperature") or self.llm_kwargs.get("temperature") or 0.1,
        )
        task.task_id = response.id
        return task

    async def _async_collect_single(self, task: BaseTask, **kwargs):
        # 准备请求对象和信息
        client = self._zhipu_client
        # 1 等待异步任务完成
        temp_response = None
        temp_task_status = "PROCESSING"
        while temp_task_status != "SUCCESS":
            await asyncio.sleep(1.5)
            if temp_task_status == "FAILED":
                warnings.warn(f"Task {task.task_id} failed!")
                temp_response = {
                    "choices": [{"message": {"content": "Task failed!"}}]
                }
                break
            temp_response = client.chat.asyncCompletions.retrieve_completion_result(task.task_id)
            temp_task_status = temp_response.task_status
        task.task_output = temp_response.choices[0].message.content
        # 2 处理重试和继续
        self._task_retry_resume(task, mode=temp_response.choices[0].finish_reason, **kwargs)
        # 3 结果解析
        try:
            task.task_result = _llm_output_parser(task.task_output, engine_json_output=self.json_output, **kwargs)
            task.task_status = "SUCCESS"
        except UserWarning:
            warnings.warn(f"Failed to parse : {task.task_output}")
            task.task_status = "PARSING_FAILED"
            task.task_result = {"output": task.task_output, "result": task.task_result}
        # 进度条递增
        if self._progress_bar:
            self._progress_bar.update(1)
        return task

    async def _async_execute(self, tasks: BaseTask | List[BaseTask], **kwargs):
        if isinstance(tasks, BaseTask):
            await self._async_submit_single(tasks, **kwargs)
            result = await self._async_collect_single(tasks, **kwargs)
            return result
        elif isinstance(tasks, List):
            # 创建一个信号量，限制并发数量为5
            semaphore = asyncio.Semaphore(int(os.getenv("THREADS_NUM", 5)))
            # 设定任务函数
            async def submit_with_semaphore(task):
                async with semaphore:
                    return await self._async_submit_single(task, **kwargs)
            # 并发执行所有提交任务
            submit_tasks = [submit_with_semaphore(task) for task in tasks]
            await asyncio.gather(*submit_tasks)
            # 设定任务函数
            async def collect_with_semaphore(task):
                async with semaphore:
                    return await self._async_collect_single(task, **kwargs)
            # 并发执行所有收集任务
            collect_tasks = [collect_with_semaphore(task) for task in tasks]
            results = await asyncio.gather(*collect_tasks)
            return results

    def _task_retry_resume(self,
                           task: BaseTask,
                           mode: str,
                           retry_on_error: bool = False,
                           **kwargs):
        """
        处理任务的重试和继续，默认情况下不会开启该服务，需要用户调用execute_task时设置retry_on_err=True
        mode: stop(async/sync) | length(async/sync) | network_error(sync) | sensitive(sync) | tool_calls(sync)
        """
        if not retry_on_error or mode == "stop":
            return
        if mode in ["length"]:
            client = self._zhipu_client
            history_msg = [
                {"role": "system", "content": task.task_system_prompt},
                {"role": "user", "content": task.task_user_prompt},
                {"role": "assistant", "content": task.task_output},
            ]
            temp_output = task.task_output
            # 继续发送任务请求
            while True:
                # 1 发出请求
                history_msg.append({"role": "user", "content": "请你继续直接接着上一句话。"})
                client = client
                response = client.chat.completions.create(
                    model=self.llm_name,
                    messages=history_msg,
                    temperature=kwargs.get("temperature") or self.llm_kwargs.get("temperature") or 0.1,
                )
                # 2 获取结果
                temp_output += response.choices[0].message.content  # 文本结果
                # 3 检查是否完成
                #if response.choices[0].finish_reason != 'length':
                task.task_output = temp_output
                break
                # 4 准备下一轮对话，将上一次的回复作为新的系统提示，并添加用户提示
                history_msg.append({"role": "assistant", "content": response.choices[0].message.content})
                history_msg.append({"role": "user", "content": "请你继续直接接着上一句话。"})
            return task


def _llm_output_parser(raw_str: str, **kwargs) -> Any:
    ret = None
    json_output_flag = kwargs.get("json_output", kwargs.get("engine_json_output"))
    if json_output_flag:
        try:
            ret = _parse_to_json(raw_str)
        except UserWarning:
            # 尝试修复json字符串
            raw_str = raw_str.replace("\n", "").replace(" ", "")
    # 如果有自定义的输出解析函数
    if kwargs.get("output_parser"):
        ret = kwargs.get("output_parser")(ret or raw_str)
    return ret


def _parse_to_json(raw_str: str) -> dict:
    # 0 所有的单反斜杠转为双反斜杠
    raw_str = raw_str.replace("\\", "\\\\")
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
        return _extract_json_code_block(raw_str)
    except Exception as e3:
        exceptions.append(e3)
    # 如果所有尝试都失败了，抛出UserWarning
    raise UserWarning(f"Failed to parse to json: {raw_str}") from exceptions[0] if exceptions else None


def _extract_json_code_block(raw_str: str):
    # Regular expression to match ```json ... ```
    pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
    # Find all matches
    matches = pattern.findall(raw_str)
    return json.loads(matches[0])


def _refined_fix_json(json_string):
    parts = json_string.split('},')
    valid_parts = []

    for part in parts:
        # Try to fix incomplete JSON objects by adding missing closing braces
        if not part.endswith('}'):
            part += '}'

        try:
            # Check if the part is a valid JSON object
            json_obj = json.loads(part)
            if json_obj not in valid_parts:  # Check for duplicates
                valid_parts.append(json_obj)
        except json.JSONDecodeError:
            # If it's not a valid JSON object, we skip it
            continue

    # Convert the list of valid JSON objects back to a JSON string
    return json.dumps(valid_parts)


####################################################################################################
# Embeddings Model
####################################################################################################
class EmbeddingsZhipuAI(BaseTextEmbeddings):
    _zhipu_client: ZhipuAI | None = None
    _progress_bar: tqdm | None = None

    @model_validator(mode="after")
    def create_zhipu_client(self):
        self._zhipu_client = ZhipuAI(api_key=self.api_key)
        return self

    def execute_embeddings(self, text: str | list, mode="sync", **kwargs):
        if mode == "sync":
            return self._sync_execute(text, **kwargs)
        elif mode == "async":
            warnings.warn("Async mode is not supported for embeddings task.")
            return self._sync_execute(text, **kwargs)

    def _sync_execute(self, text: str | list, **kwargs) -> list[list] | list:
        client = self._zhipu_client
        responses: list[dict] = client.embeddings.create(
            model=self.embeddings_name,
            input=text,
            dimensions=kwargs.get("dimensions") or self.embeddings_kwargs.get("dimensions") or 2048
        )["data"]
        if isinstance(text, str):
            # 如果只输入了一个字符串，则对应一个嵌入
            return responses[0]["embedding"]
        elif isinstance(text, list):
            # 如果输入了多个字符串，则对应多个嵌入，多个嵌入组成一个列表
            return [response["embedding"] for response in responses]
        else:
            warnings.warn(f"Unexpected input type: {type(text)}, the response is unknown but returned still.")
            return responses
