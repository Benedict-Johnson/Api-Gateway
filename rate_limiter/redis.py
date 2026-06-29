import redis.asyncio as redis


class RedisClient:

    def __init__(self):
        self.client = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True
        )

    async def get(self, name):
        return await self.client.get(name)

    async def set(self, name, value, ex=None):
        return await self.client.set(name, value, ex=ex)

    async def incr(self, name):
        return await self.client.incr(name)

    async def expire(self, name, time):
        return await self.client.expire(name, time)

    async def hset(self, name, key=None, value=None, mapping=None):
        return await self.client.hset(name, key, value, mapping)

    async def hgetall(self, name):
        return await self.client.hgetall(name)

    async def zadd(self, name, mapping):
        return await self.client.zadd(name, mapping)

    async def zcard(self, name):
        return await self.client.zcard(name)

    async def zremrangebyscore(self, name, min, max):
        return await self.client.zremrangebyscore(name, min, max)


redis_client = RedisClient()