from cache.config import CacheConfigLoader
from cache.key_builder import key_builder
from cache.redis import cache_redis
from observability.logger import logger


class CacheManager:

    def __init__(self):

        self.config = CacheConfigLoader(
            "cache/config.yaml"
        ).config

    async def get(self, request):

        key = key_builder.build(request)

        return await cache_redis.client.get(key)

    async def set(self, request, response):

        key = key_builder.build(request)

        logger.debug(f"Cache SET {key}")

        await cache_redis.client.setex(
            key,
            self.config.default_ttl,
            response,
        )

        value = await cache_redis.client.get(key)

        logger.debug(f"Redis returned: {value is not None}")
    
    async def invalidate(self, request):

        paths = self.config.invalidate.get(
            request.method,
            [],
        )

        if request.url.path in paths:
            keys = await cache_redis.client.keys(
                f"GET:{request.url.path}*"
            )

            if keys:
                await cache_redis.client.delete(
                    *keys
                )
                logger.info(f"Invalidated cache keys: {keys}")


cache_manager = CacheManager()