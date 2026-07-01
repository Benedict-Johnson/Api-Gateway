import asyncio

import httpx

from config.retry import RetryLoader
from observability.context import retry_count_var, service_name_var
from observability.logger import logger
from observability.metrics import GATEWAY_RETRY_TOTAL, GATEWAY_TIMEOUT_TOTAL


class RetryPolicy:
    def __init__(self, path: str = "config/retry.yaml"):
        self.config = RetryLoader(path).config

    async def execute(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        headers: dict,
        params: dict,
        content: bytes,
    ):
        for attempt in range(self.config.attempts):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    content=content,
                )

                if response.status_code in self.config.retry_on:
                    raise httpx.HTTPStatusError(
                        "Retry",
                        request=response.request,
                        response=response,
                    )

                return response

            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                service = service_name_var.get()

                if isinstance(e, httpx.TimeoutException):
                    GATEWAY_TIMEOUT_TOTAL.labels(service=service).inc()

                if attempt == self.config.attempts - 1:
                    raise e

                GATEWAY_RETRY_TOTAL.labels(service=service).inc()
                retry_count_var.set(attempt + 1)

                logger.warning(
                    f"Retry attempt {attempt + 1}/{self.config.attempts} for {url}"
                )
                await asyncio.sleep(self.config.backoff * (2**attempt))
