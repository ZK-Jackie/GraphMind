import re
import warnings
from typing import List, Any, Coroutine
from tqdm import tqdm

from zhipuai import ZhipuAI

from chatkg.adapter.structure.base import BaseTask
from chatkg.adapter.task_model.base import BaseTaskModel

import time
import json
import asyncio


class TaskZhipuAI(BaseTaskModel):
    json_output: bool = True
    _zhipu_client: ZhipuAI | None = None
    _progress_bar: tqdm | None = None

    def execute_task(self,
                     task: BaseTask | List[BaseTask],
                     mode="async",
                     **kwargs) -> Coroutine[Any, Any, BaseTask | list[BaseTask]] | BaseTask | tuple[Any]:
        # 1 client
        self._zhipu_client = ZhipuAI(api_key=self.api_key)
        # 2 进度条
        # TODO 换成装饰器围绕递增的进度条
        self._progress_bar = kwargs.get("progress_bar")
        # 3 执行任务
        if mode == "sync":
            return self._execute_sync(task, **kwargs)
        elif mode == "async":
            return asyncio.run(self._execute_async(task, **kwargs))


    def _submit_sync_single(self, task: BaseTask, **kwargs):
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
            task.task_output = parse_to_json(task.task_output)
        return task

    async def _execute_sync(self, task: BaseTask | List[BaseTask], **kwargs) -> BaseTask | List[BaseTask]:
        if isinstance(task, BaseTask):
            return self._submit_sync_single(task, **kwargs)
        elif isinstance(task, List):
            for task in task:
                self._submit_sync_single(task, **kwargs)
            return task

    async def _submit_async_single(self, task: BaseTask, **kwargs):
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

    async def _collect_async_single(self, task: BaseTask, **kwargs):
        client = self._zhipu_client
        # 等待异步任务完成
        temp_response = None
        temp_task_status = "PROCESSING"
        while temp_task_status != "SUCCESS":
            time.sleep(2)
            if temp_task_status == "FAILED":
                warnings.warn(f"Task {task.task_id} failed!")
                temp_response = {
                    "choices": [
                        {
                            "message": {
                                "content": "Task failed!"
                            }
                        }
                    ]
                }
                break
            temp_response = client.chat.asyncCompletions.retrieve_completion_result(task.task_id)
            temp_task_status = temp_response.task_status
        task.task_output = temp_response.choices[0].message.content
        if self.json_output:
            task.task_output = parse_to_json(task.task_output)
        if self._progress_bar:
            self._progress_bar.update(1)
        return task

    async def _execute_async(self, tasks: BaseTask | List[BaseTask], **kwargs):
        if isinstance(tasks, BaseTask):
            await self._submit_async_single(tasks, **kwargs)
            result = await self._collect_async_single(tasks, **kwargs)
            return result
        elif isinstance(tasks, List):
            # 创建任务列表来异步执行提交操作
            submit_tasks = [self._submit_async_single(task, **kwargs) for task in tasks]
            # 等待所有提交操作完成
            await asyncio.gather(*submit_tasks)
            # 创建任务列表来异步执行收集操作
            collect_tasks = [self._collect_async_single(task, **kwargs) for task in tasks]
            # 等待所有收集操作完成并获取结果
            results = await asyncio.gather(*collect_tasks)
            return results


def parse_to_json(raw_str: str) -> dict:
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
                out = extract_json_code_block(raw_str)
            except Exception as e3:
                # 若都失败，返回原始字符串
                out = {
                    "raw": raw_str
                }
                warnings.warn(f"Failed to parse to json: {raw_str}")
    return out


def extract_json_code_block(raw_str: str):
    # Regular expression to match ```json ... ```
    pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
    # Find all matches
    matches = pattern.findall(raw_str)
    return json.loads(matches[0])
