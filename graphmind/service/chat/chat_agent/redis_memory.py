from graphmind.service.chat.chat_agent.memory.redis import RedisSaver
from graphmind.service.databases.redis_db import redis_client


redis_saver = RedisSaver(redis_client)

__all__ = ["redis_saver"]