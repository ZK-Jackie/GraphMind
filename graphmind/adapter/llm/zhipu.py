import re
import warnings
from typing import List, Any, Coroutine

from pydantic import model_validator, Field
from tqdm import tqdm

from zhipuai import ZhipuAI

from graphmind.adapter.structure.base import BaseTask
from graphmind.adapter.llm.base import BaseTaskLLM, BaseTextEmbeddings

import time
import json
import asyncio

####################################################################################################
# Chat model
####################################################################################################
class TaskZhipuAI(BaseTaskLLM):
    json_output: bool = Field(description="Whether to parse the output to json", default=False)
    _zhipu_client: ZhipuAI | None = Field(description="ZhipuAI client", default=None)
    _progress_bar: tqdm | None = Field(description="Progress bar from caller", default=None)

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

    def _sync_submit_single(self, task: BaseTask, **kwargs):
        client = self._zhipu_client
        response = client.chat.completions.create(
            model=self.llm_name,
            messages=[
                {"role": "system", "content": task.task_system_prompt},
                {"role": "user", "content": task.task_user_prompt},
            ]
        )
        task.task_output = response.choices[0].message.content
        if self.json_output:
            task.task_output = _parse_to_json(task.task_output)
        return task

    def _sync_execute(self, task: BaseTask | List[BaseTask], **kwargs) -> BaseTask | List[BaseTask]:
        if isinstance(task, BaseTask):
            return self._sync_submit_single(task, **kwargs)
        elif isinstance(task, List):
            for task in task:
                self._sync_submit_single(task, **kwargs)
            return task

    async def _async_submit_single(self, task: BaseTask, **kwargs):
        client = self._zhipu_client
        # 异步、任务式请求
        response = client.chat.asyncCompletions.create(
            model=self.llm_name,
            messages=[
                {"role": "system", "content": task.task_system_prompt},
                {"role": "user", "content": task.task_user_prompt},
            ]
        )
        task.task_id = response.id
        return task

    async def _async_collect_single(self, task: BaseTask, **kwargs):
        client = self._zhipu_client
        # 等待异步任务完成
        temp_response = None
        temp_task_status = "PROCESSING"
        while temp_task_status != "SUCCESS":
            time.sleep(2)
            if temp_task_status == "FAILED":
                warnings.warn(f"Task {task.task_id} failed!")
                temp_response = {
                    "choices": [{"message": {"content": "Task failed!"}}]
                }
                break
            temp_response = client.chat.asyncCompletions.retrieve_completion_result(task.task_id)
            temp_task_status = temp_response.task_status
        task.task_output = temp_response.choices[0].message.content
        if self.json_output:
            task.task_output = _parse_to_json(task.task_output)
        if self._progress_bar:
            self._progress_bar.update(1)
        return task

    async def _async_execute(self, tasks: BaseTask | List[BaseTask], **kwargs):
        if isinstance(tasks, BaseTask):
            await self._async_submit_single(tasks, **kwargs)
            result = await self._async_collect_single(tasks, **kwargs)
            return result
        elif isinstance(tasks, List):
            # 创建任务列表来异步执行提交操作
            submit_tasks = [self._async_submit_single(task, **kwargs) for task in tasks]
            # 等待所有提交操作完成
            await asyncio.gather(*submit_tasks)
            # 创建任务列表来异步执行收集操作
            collect_tasks = [self._async_collect_single(task, **kwargs) for task in tasks]
            # 等待所有收集操作完成并获取结果
            results = await asyncio.gather(*collect_tasks)
            return results


# TODO 使用 pydantic + langchain 重写该类
def _parse_to_json(raw_str: str) -> dict:
    try:
        # 把 json 字符串转换为字典
        out = json.loads(raw_str)
    except Exception as e1:
        # 若生成markdown代码块字符串，需要从代码块中提取json字符串
        try:
            # 从代码块中提取json字符串
            out = json.loads(raw_str.split("```")[1])
        except Exception as e2:
            try:
                # 从代码块中提取json字符串
                out = _extract_json_code_block(raw_str)
            except Exception as e3:
                # 若都失败，返回原始字符串
                out = {"raw": raw_str}
                warnings.warn(f"Failed to parse to json: {raw_str}")
    return out


def _extract_json_code_block(raw_str: str):
    # Regular expression to match ```json ... ```
    pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
    # Find all matches
    matches = pattern.findall(raw_str)
    return json.loads(matches[0])


####################################################################################################
# Embeddings
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
