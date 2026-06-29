import asyncio
import time

from load_balancer.discovery.registry import registry


EXPIRATION_TIME = 30
CHECK_INTERVAL = 10


class CleanupManager:

    async def run(self):

        while True:

            now = time.time()

            for service in list(registry.services.keys()):

                registry.services[service] = [

                    instance

                    for instance in registry.services[service]

                    if now - instance.last_seen < EXPIRATION_TIME

                ]

            await asyncio.sleep(CHECK_INTERVAL)


cleanup_manager = CleanupManager()