import httpx

from gateway.resilience.circuit_breaker import CircuitBreakerPolicy
from gateway.resilience.retry import RetryPolicy
from gateway.resilience.timeout import TimeoutPolicy


class ResilienceManager:
    def __init__(self):
        self.timeout_policy = TimeoutPolicy()
        self.retry_policy = RetryPolicy()
        self.circuit_breaker = CircuitBreakerPolicy()
        self.client = httpx.AsyncClient(timeout=self.timeout_policy.get_httpx_timeout())

    async def execute(
        self,
        service_name: str,
        method: str,
        url: str,
        headers: dict,
        params: dict,
        content: bytes,
    ) -> httpx.Response:
        return await self.circuit_breaker.execute(
            retry_policy=self.retry_policy,
            client=self.client,
            service_name=service_name,
            method=method,
            url=url,
            headers=headers,
            params=params,
            content=content,
        )
