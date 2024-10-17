from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from graphmind.service.chat import agent_invoke, agent_stream
from graphmind.service.chat.base import ChatMessage

api_chat = APIRouter()

@api_chat.post("/test")
async def test():
    return {"code": "200", "msg": "ok", "data": "hello, world!"}

@api_chat.post("/invoke")
async def post_chat(chat_input: ChatMessage) -> ChatMessage:
    return agent_invoke(chat_input)

@api_chat.post("/stream")
async def chat(chat_input: ChatMessage):
    async def event_generator():
        async for chunk in agent_stream(chat_input):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")


