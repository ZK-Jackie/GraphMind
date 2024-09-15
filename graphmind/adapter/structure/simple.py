from pydantic import Field

from graphmind.adapter.structure import BaseTask, BaseTaskResult

class SimpleResult(BaseTaskResult):
    result: str | None = Field(description="Result", default=None)

    def dump_dict(self):
        pass


class SimpleTask(BaseTask):
    task_result: SimpleResult | None = None

