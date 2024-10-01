from redis import Redis

from graphmind.service.agent_build.memory.redis import RedisSaver
from graphmind.service.config.redis import RedisConfig


redis_memory = RedisSaver(Redis(host=RedisConfig.REDIS_HOST, port=RedisConfig.REDIS_PORT, db=RedisConfig.REDIS_DB))

__all__ = ["redis_memory"]