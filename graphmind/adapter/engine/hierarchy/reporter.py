from typing import Iterable

from rich.console import Console
from rich.live import Live
from rich.progress import Progress, TaskID

from graphmind.core.base import BaseReporter


class GraphmindReporter(BaseReporter):
    # 状态属性
    _prefix: str  # 当前工作名称
    _disposing: bool = False  # 当前销毁状态
    # 进度条属性
    _progressbar: Progress | None = None  # 进度条对象
    _console: Console
    _live: Live
    _task: TaskID | None = None  # 任务 ID
    # 父级对象属性
    _parent: "GraphmindReporter | None" = None
    _workflows: dict[str, "GraphmindReporter"] = {}
    # 进度信息属性
    _now_completed: int = -1    # 任务开始时汇报一次
    _total_items: int = 0

    @property
    def console(self) -> Console:
        return self._console

    @property
    def live(self) -> Live:
        return self._live

    def dispose(self) -> None:
        """取消进度条"""
        self._disposing = True
        if self._progressbar is not None:
            self._progressbar.stop()

    def __init__(self,
                 prefix: str,
                 parent: "GraphmindReporter" = None,
                 total_items: int = 0):
        # 初始化属性
        self._prefix = prefix
        self._total_items = total_items
        # 如果有父级对象，则创建进度条
        if parent:
            self._console = parent.console
            self._parent = parent
            self._live = parent.live
            self._progressbar = Progress(console=self._console)
            self._task = self._progressbar.add_task(prefix, total=total_items)
            self.update(1)  # 任务开始时汇报一次
        else:
            # 如果当前是顶级对象，仅作为标题显示
            self._console = Console()
            self._live = Live(console=self._console, refresh_per_second=1)
            self._live.start()
            self._parent = None
            print(prefix)

    def add_workflow(self, prefix: str, total_items: int = 0) -> "GraphmindReporter":
        """添加工作流"""
        self._workflows[prefix] = GraphmindReporter(prefix, self, total_items)
        return self._workflows[prefix]

    def update(self, increment: int = 1) -> None:
        """更新进度条"""
        # 如果当前对象已经被销毁，则不再更新
        if self._disposing:
            return
        # 如果当前对象是顶级对象，则不再更新
        if self._parent is None:
            return
        # 如果进度没有变化，则不再更新
        new_completed = self._now_completed + increment
        if new_completed == self._now_completed:
            return
        # 更新进度条
        self._now_completed = new_completed
        if self._now_completed <= self._total_items:
            self._progressbar.update(self._task, completed=self._now_completed)
        else:
            self._now_completed = self._total_items
        # 汇报进度
        print(f"{self._prefix} - {self._now_completed}/{self._total_items}", flush=True)

    def __call__(self, iterable: Iterable, increment: int = 1):
        """更新进度并返回一个生成器"""
        for any_iter in iterable:
            self.update(increment)
            yield any_iter
