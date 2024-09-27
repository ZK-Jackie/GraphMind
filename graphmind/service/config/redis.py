import os


class RedisConfig:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    """Redis数据库连接信息，默认为本地连接"""

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    """Redis数据库主机地址，默认为本地"""

    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    """Redis数据库端口，默认为6379"""

    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    TTL: int | None = None
    """消息历史的存活时间，默认永久保存"""
