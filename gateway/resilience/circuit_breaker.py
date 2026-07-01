import asyncio
import time
from enum import Enum

import httpx

from config.circuit_breaker import CircuitBreakerLoader
from observability.context import circuit_state_var
from observability.logger import logger
from observability.metrics import GATEWAY_CIRCUIT_OPEN_TOTAL


class CircuitOpenException(Exception):
    pass


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(self, service_name: str, config):
        self.service_name = service_name
        self.config = config

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = 0
        self.half_open_in_progress = False
        self.lock = asyncio.Lock()

    async def get_state(self):
        if self.state == CircuitState.OPEN:
            if time.time() - self.opened_at >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit HALF_OPEN for {self.service_name}")
        return self.state

    async def record_failure(self):
        async with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.opened_at = time.time()
                self.half_open_in_progress = False
                GATEWAY_CIRCUIT_OPEN_TOTAL.labels(service=self.service_name).inc()
                logger.warning(f"Circuit REOPENED for {self.service_name}")
            else:
                self.failure_count += 1
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    self.opened_at = time.time()
                    GATEWAY_CIRCUIT_OPEN_TOTAL.labels(service=self.service_name).inc()
                    logger.warning(f"Circuit OPEN for {self.service_name}")

    async def record_success(self):
        async with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.opened_at = 0
                    self.half_open_in_progress = False
                    logger.info(f"Circuit CLOSED for {self.service_name}")
                else:
                    self.half_open_in_progress = False
            else:
                self.failure_count = 0

    async def allow_request(self) -> bool:
        if not self.config.enabled:
            return True

        async with self.lock:
            current_state = await self.get_state()
            if current_state == CircuitState.OPEN:
                logger.debug(f"Rejecting request to {self.service_name} (Circuit OPEN)")
                return False
            if current_state == CircuitState.HALF_OPEN:
                if self.half_open_in_progress:
                    logger.debug(
                        f"Rejecting request to {self.service_name} (Circuit HALF_OPEN concurrent lock)"
                    )
                    return False
                self.half_open_in_progress = True
                return True
            return True


class CircuitBreakerPolicy:
    def __init__(self, path: str = "config/circuit_breaker.yaml"):
        self.config = CircuitBreakerLoader(path).config
        self.breakers = {}
        self.lock = asyncio.Lock()

    async def get_breaker(self, service_name: str) -> CircuitBreaker:
        async with self.lock:
            if service_name not in self.breakers:
                self.breakers[service_name] = CircuitBreaker(service_name, self.config)
            return self.breakers[service_name]

    async def execute(
        self, retry_policy, client, service_name, method, url, headers, params, content
    ):
        breaker = await self.get_breaker(service_name)

        current_state = await breaker.get_state()
        circuit_state_var.set(current_state.value)

        if not await breaker.allow_request():
            raise CircuitOpenException()

        try:
            response = await retry_policy.execute(
                client, method, url, headers, params, content
            )
            await breaker.record_success()
            return response

        except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
            await breaker.record_failure()
            raise e
