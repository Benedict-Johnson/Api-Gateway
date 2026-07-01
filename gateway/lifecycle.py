import asyncio
import time

from config.shutdown import ShutdownLoader
from observability.logger import logger


class LifecycleManager:
    def __init__(self):
        self.config = ShutdownLoader("config/shutdown.yaml").config
        self.shutting_down = False
        self.active_requests = 0
        self._lock = asyncio.Lock()

    async def increment_requests(self):
        async with self._lock:
            self.active_requests += 1

    async def decrement_requests(self):
        async with self._lock:
            self.active_requests -= 1

    async def trigger_shutdown(self):
        logger.info("[SHUTDOWN] Received SIGTERM")
        self.shutting_down = True

        if not self.config.enabled:
            logger.info("[SHUTDOWN] Graceful shutdown disabled, exiting immediately")
            return

        start_time = time.time()

        while self.active_requests > 0:
            elapsed = time.time() - start_time
            if elapsed >= self.config.graceful_timeout:
                logger.warning(
                    f"[SHUTDOWN] Graceful timeout ({self.config.graceful_timeout}s) reached with {self.active_requests} requests still active."
                )
                break

            logger.info(
                f"[SHUTDOWN] Waiting for {self.active_requests} active requests"
            )
            await asyncio.sleep(1)

        if self.active_requests <= 0:
            logger.info("[SHUTDOWN] All requests completed")

        logger.info("[SHUTDOWN] Gateway stopped")


lifecycle_manager = LifecycleManager()
