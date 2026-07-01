import asyncio

import pytest

from cache.manager import cache_manager


class Request:

    method = "GET"

    class URL:

        path = "/users"

        query = ""

    url = URL()


async def main():

    await cache_manager.set(
        Request(),
        b"hello",
    )

    value = await cache_manager.get(Request())

    print(value)


@pytest.mark.anyio
async def test_cache_manager():
    class TestReq:
        method = "GET"

        class URL:
            path = "/test-cache-unit"
            query = ""

        url = URL()

    req = TestReq()
    await cache_manager.set(req, b"hello_pytest")
    val = await cache_manager.get(req)
    assert val == b"hello_pytest"
    from cache.redis import cache_redis
    try:
        await cache_redis.client.close()
    except Exception:
        pass
    cache_redis.__init__()


if __name__ == "__main__":
    asyncio.run(main())
