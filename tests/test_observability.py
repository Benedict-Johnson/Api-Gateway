import asyncio

import httpx

from config.settings import settings


async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Check Health
        res = await client.get("/health")
        print("Health Response:", res.status_code)
        print(res.json())

        # Check Live
        res = await client.get("/live")
        print("Live Response:", res.status_code, res.json())

        # Check Ready
        res = await client.get("/ready")
        print("Ready Response:", res.status_code, res.json())

        # Make a few requests to populate metrics
        for _ in range(5):
            await client.get("/users", headers={"X-API-Key": settings.API_KEY_SECRET})

        # Trigger rate limit
        for _ in range(15):
            await client.get("/slow", headers={"X-API-Key": settings.API_KEY_SECRET})

        # Trigger an error (invalid route)
        await client.get("/notfound", headers={"X-API-Key": settings.API_KEY_SECRET})

        # Check metrics
        res = await client.get("/metrics")
        print("\nMetrics Output Preview:")

        # Print a few lines of the metrics output that start with gateway_
        lines = [line for line in res.text.split("\n") if line.startswith("gateway_")]
        for line in lines[:20]:
            print(line)


if __name__ == "__main__":
    asyncio.run(main())
