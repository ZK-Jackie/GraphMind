import os

from pydantic import ConfigDict


class RedisConfig:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    """Redis数据库连接信息，默认为本地连接"""

    TTL: int | None = None
    """消息历史的存活时间，默认永久保存"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """允许任意类型的配置字典"""