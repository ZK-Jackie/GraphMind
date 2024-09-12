"""
此包预计放自己做了封装之后的ZhipuAI、OpenAI、InternLM、transformer.from_pretrained等等之类的类
"""
from graphmind.adapter.llm.base import BaseTaskLLM
from graphmind.adapter.llm.zhipu import TaskZhipuAI, EmbeddingsZhipuAI

__all__ = ["BaseTaskLLM",

           "TaskZhipuAI",
           "EmbeddingsZhipuAI"]