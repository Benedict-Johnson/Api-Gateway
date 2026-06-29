import asyncio

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

    value = await cache_manager.get(

        Request()

    )

    print(value)


asyncio.run(main())