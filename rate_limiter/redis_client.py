import redis.asyncio as redis


class RedisClient:

    def __init__(self):
        self.client = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True
        )


redis_client = RedisClient()