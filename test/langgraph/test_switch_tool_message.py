from dotenv import load_dotenv

load_dotenv()
from graphmind.service.chat.chat_agent.agent import GraphAgent

graph = GraphAgent().agent_with_history

config = {"configurable": {"thread_id": "user-Test_conv-1"}}

snapshot = graph.get_state(config)
