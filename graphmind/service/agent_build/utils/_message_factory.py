from langchain_core.messages import AIMessage, ToolMessage


def _create_tool_message(tool_response: str, ai_message: AIMessage) -> ToolMessage:
    return ToolMessage(
        content=tool_response,
        tool_call_id=ai_message.tool_calls[0]["id"],
    )