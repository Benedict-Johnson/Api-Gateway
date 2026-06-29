import asyncio
import httpx


URL = "http://host.docker.internal:8000/slow"

HEADERS = {
    "X-API-Key": "secret123"
}


async def send_request(client, request_id):

    response = await client.get(
        URL,
        headers=HEADERS,
    )

    print("=" * 40)
    print(f"Request {request_id}")
    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("content-type"))
    print("Body:")
    print(response.text)


async def main():

    async with httpx.AsyncClient(timeout=20) as client:

        tasks = [
            send_request(client, i)
            for i in range(20)
        ]

        await asyncio.gather(*tasks)


asyncio.run(main())