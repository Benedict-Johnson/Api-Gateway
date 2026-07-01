import redis.asyncio as redis

from config.settings import settings


class CacheRedis:

    def __init__(self):

        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=False,
        )


cache_redis = CacheRedis()
