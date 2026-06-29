import redis.asyncio as redis


class CacheRedis:

    def __init__(self):

        self.client = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=False,
        )


cache_redis = CacheRedis()