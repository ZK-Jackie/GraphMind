from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from graphmind.service.agent import agent
from graphmind.service.base import ChatMessage
from graphmind.service.chain import rag_chain

api_chat = APIRouter()

@api_chat.post("/test")
async def test():
    return {"code": "200", "msg": "ok", "data": "hello, world!"}

@api_chat.post("/invoke")
async def post_chat(chat_input: ChatMessage) -> ChatMessage:
    return agent.invoke(chat_input)

@api_chat.post("/stream")
async def chat(chat_input: ChatMessage):
    async def event_generator():
        async for chunk in agent.stream(chat_input):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")


