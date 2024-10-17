import os
from redis import Redis


class RedisConfig:
    REDIS_URL: str = (os.getenv("REDIS_URL") or
                      f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0")
    """Redis数据库连接信息，默认为本地连接"""

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    """Redis数据库主机地址，默认为本地"""

    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    """Redis数据库端口，默认为6379"""

    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    TTL: int | None = None
    """消息历史的存活时间，默认永久保存"""


redis_client = Redis(host=RedisConfig.REDIS_HOST, port=RedisConfig.REDIS_PORT, db=RedisConfig.REDIS_DB)

__all__ = ["redis_client", "RedisConfig"]
