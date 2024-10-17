from graphmind.core.base import GraphmindModelConfig
from graphmind.service.chat.chat_agent.base import QueryState
from graphmind.service.chat.chat_agent.sub_graphs.cypher_graph import CypherGraph
from graphmind.service.chat.chat_context import set_user_config
from graphmind.service.user.user_model import UserModelConfig


set_user_config(UserModelConfig(user_id="test", conv_id="1", graphmind_config=GraphmindModelConfig()))

agent = CypherGraph().agent_with_history
input_state = {
    "raw_queries": ["离散数学是什么", "闭包有哪些关联点"],
    "ask_human": False,
    "entity_finished": False,
    "type_finished": False
}
user_config = {"configurable": {"thread_id": "1"}}
result: QueryState = agent.invoke(input_state, user_config, stream_mode="values", debug=True)
print(type(result))
