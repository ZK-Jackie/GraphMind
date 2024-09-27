from typing import Literal
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from redis import Redis

from graphmind.service.agent_build.memory.redis import RedisSaver


@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")


tools = [get_weather]
model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

memory = RedisSaver(Redis(host="localhost", port=6379, db=0))

# 这个 agent 是 langgraph 预制的构建的函数，能够快速的构建一个图
# 避免自己写 agent 逻辑，官方不推荐使用（要写这个还不如用Langchain）
graph = create_react_agent(model, tools=tools, checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}
res = graph.invoke({"messages": [("human", "what's the weather in sf")]}, config)

latest_checkpoint = memory.get(config)
latest_checkpoint_tuple = memory.get_tuple(config)
checkpoint_tuples = list(memory.list(config))
