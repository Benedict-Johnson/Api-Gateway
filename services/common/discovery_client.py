import asyncio
import httpx


class DiscoveryClient:

    def __init__(
        self,
        service,
        host,
        port,
        api_key,
        gateway="http://api-gateway:8000",
    ):

        self.service = service
        self.host = host
        self.port = port
        self.api_key = api_key
        self.gateway = gateway

        self.client = httpx.AsyncClient(
            headers={
                "X-API-Key": self.api_key
            }
        )

    async def register(self):

        print(f"[DISCOVERY] Registering {self.host}:{self.port}")

        for attempt in range(10):

            try:

                response = await self.client.post(

                    f"{self.gateway}/discovery/register",

                    json={

                        "service": self.service,
                        "host": self.host,
                        "port": self.port,
                        "weight": 1,

                    },

                )

                response.raise_for_status()

                print("[DISCOVERY] Registration successful")

                return

            except Exception:

                print(
                    f"[DISCOVERY] Gateway unavailable "
                    f"(attempt {attempt + 1}/10)"
                )

                await asyncio.sleep(2)

        raise RuntimeError(
            "Unable to register service."
        )

    async def heartbeat(self):

        while True:

            print(f"[DISCOVERY] Heartbeat {self.host}:{self.port}")

            try:

                await self.client.post(

                    f"{self.gateway}/discovery/heartbeat",

                    json={

                        "service": self.service,
                        "host": self.host,
                        "port": self.port,

                    },

                )

            except Exception:

                print("[DISCOVERY] Heartbeat failed")

            await asyncio.sleep(10)

    async def deregister(self):

        print(f"[DISCOVERY] Deregistering {self.host}:{self.port}")

        try:

            await self.client.request(

                "DELETE",

                f"{self.gateway}/discovery/deregister",

                json={

                    "service": self.service,
                    "host": self.host,
                    "port": self.port,

                },

            )

        except Exception:

            print("[DISCOVERY] Deregistration failed")
    
    async def run(self):

        while True:

            try:

                await self.register()

                await self.heartbeat()

            except Exception as e:

                print(f"[DISCOVERY] {e}")

                await asyncio.sleep(2)