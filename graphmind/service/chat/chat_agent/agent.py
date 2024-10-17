import logging
from typing import Generator
from typing_extensions import Self, Literal

from pydantic import BaseModel, Field, model_validator, ConfigDict

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.constants import START, END

from graphmind.service.chat.chat_agent.base import State
from graphmind.service.chat.chat_agent.prompts import summary, judge
from graphmind.service.chat.chat_agent.redis_memory import redis_saver
from graphmind.service.chat.chat_agent.sub_graphs import knowledge_search_tool_node
from graphmind.service.chat.chat_agent.tools import tool_name_list, tool_list
from graphmind.service.chat.base import ChatMessage
from graphmind.service.chat.chat_reporter import status_report
from graphmind.service.user.user_model import context_session_id, context_llm

logger = logging.getLogger(__name__)


class GraphAgent(BaseModel):
    agent_with_history: CompiledStateGraph | None = Field(description="Chat agent with message history",
                                                          default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def create_agent(self) -> Self:
        graph_builder = StateGraph(State)

        graph_builder.add_node("judge", self._judge_bot)
        graph_builder.add_node("knowledge_search_tool", knowledge_search_tool_node)
        graph_builder.add_node("Inquiry", self._inquiry_switch_node)
        graph_builder.add_node("summary", self._final_bot)

        graph_builder.add_edge(START, "judge")
        graph_builder.add_conditional_edges(
            "judge",
            self._condition_choose_tool
            # 第三个参数 path_map 中，键是 condition 函数的返回值，值是节点真实名字
        )
        for tool_name in tool_name_list:
            graph_builder.add_edge(tool_name, "summary")

        graph_builder.add_edge("summary", END)

        self.agent_with_history = graph_builder.compile(checkpointer=redis_saver)

        logger.info("LangGraph agent created.")
        return self

    def invoke(self, user_message: ChatMessage) -> ChatMessage:
        # 从 ChatMessage 对象中获取 AI 消息模板
        ai_message = user_message.get_ai_message()
        # 从上下文 user_config 中获取 session_id；如果不存在，报错
        session_id = context_session_id()
        if session_id is None:
            raise RuntimeError("Error when validating user configuration.")
        # 准备输入变量，调用 agent
        input_state = {
            "messages": [user_message.content],
            "ask_human": False,
            "override_message": False
        }
        user_config = {"configurable": {"thread_id": session_id}}
        ai_message.content = self.agent_with_history.invoke(input_state, user_config, stream_mode="values")
        logger.info(f"Invoking AI message: {ai_message.model_dump()}")
        return ai_message

    def stream(self, user_message: ChatMessage) -> Generator[ChatMessage, None, None]:
        # 从 ChatMessage 对象中获取 AI 消息模板
        ai_message = user_message.get_ai_message()
        # 从上下文 user_config 中获取 session_id；如果不存在，报错
        session_id = context_session_id()
        if session_id is None:
            raise RuntimeError("Error when validating user configuration.")
        # 准备输入变量，调用 agent
        input_state = {
            "messages": [user_message.content],
            "ask_human": False,
            "override_message": False
        }
        user_config = {"configurable": {"thread_id": session_id}}
        chunks = self._graph_str_stream(input_state, user_config)
        for chunk in chunks:
            # 根据需求返回对应的格式的信息
            if user_message.chunk_resp:
                ai_message.content = chunk
            else:
                ai_message.content += chunk
            yield ai_message
        logger.info(f"Streaming AI message: {ai_message.model_dump()}")

    def _graph_str_stream(self, input_state: dict, user_config: dict) -> Generator[str, None, None]:
        stream_result = self.agent_with_history.stream(input_state, user_config, stream_mode="messages")
        for msg, metadata in stream_result:
            if (msg.content
                    and not isinstance(msg, HumanMessage)
                    and not isinstance(msg, ToolMessage)
                    and metadata["langgraph_node"] == "summary"
            ):
                yield msg.content

    @staticmethod
    @status_report("分析用户问题")
    def _judge_bot(state: State):
        messages = [SystemMessage(judge.system_prompt)]
        messages.extend(state.get("messages", []))
        prompt_template = ChatPromptTemplate.from_messages(
            messages
        )
        llm_with_tools = context_llm().bind_tools(tool_list)
        judge_chain = prompt_template | llm_with_tools
        logger.info(f"Using Judge Bot")
        return {"messages": [judge_chain.invoke({})]}

    @staticmethod
    def _condition_choose_tool(state: State) -> Literal["knowledge_search_tool", "Inquiry", "__end__"]:
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            # 从 state 中获取 messages 的值，如果 messages 存在且非空，则赋值给 messages，执行代码块
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if len(ai_message.tool_calls) > 0 and ai_message.tool_calls[0] and ai_message.tool_calls[0][
            "name"] in tool_name_list:
            # 如果要调用工具，且工具名在 tool_name_list 中，则返回工具名
            if ai_message.tool_calls[0]["name"] == "knowledge_search_tool":
                return "knowledge_search_tool"
            elif ai_message.tool_calls[0]["name"] == "Inquiry":
                return "Inquiry"
        return "__end__"

    @staticmethod
    def _inquiry_switch_node(state: State):
        logger.info(f"Using Inquiry Switch Node")
        return {"override_message": True}

    @staticmethod
    @status_report("总结上下文并回答用户", final_report=True)
    def _final_bot(state: State):
        messages = [SystemMessage(summary.system_prompt)]
        messages.extend(state.get("messages", []))
        if state.get("override_message") and messages[-1].type == "tool":
            messages = messages[:-1]
        prompt_template = ChatPromptTemplate.from_messages(
            messages
        )
        llm_with_tools = context_llm().bind_tools(tool_list)
        summary_chain = prompt_template | llm_with_tools
        logger.info(f"Using Final Bot")
        return {"messages": [summary_chain.invoke({})]}


agent = GraphAgent()

__all__ = ["agent"]
