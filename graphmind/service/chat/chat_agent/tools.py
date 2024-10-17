from pydantic import BaseModel

from graphmind.service.chat.chat_agent.sub_graphs.cypher_graph import knowledge_search_tool

class Inquiry(BaseModel):
    """Useful when no other suitable tool is found

    """

tool_list = [knowledge_search_tool, Inquiry]
tool_name_list = ["knowledge_search_tool", "Inquiry"]

__all__ = ["tool_list", "tool_name_list"]