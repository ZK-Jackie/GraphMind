import redis


def get_value(key: str) -> str:
    """
    从 Redis 获取值

    Returns:
        str: Redis 中的值

    """
    r = redis.Redis()
    return r.get(key) or ""
