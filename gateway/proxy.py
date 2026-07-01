import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, Response

from gateway.resilience.circuit_breaker import CircuitOpenException
from gateway.resilience.manager import ResilienceManager


class ReverseProxy:

    def __init__(self):
        self.resilience_manager = ResilienceManager()

    async def forward(
        self,
        request: Request,
        target_url: str,
        service_name: str,
    ):

        body = await request.body()

        try:
            response = await self.resilience_manager.execute(
                service_name=service_name,
                method=request.method,
                url=target_url,
                headers=request.headers,
                params=request.query_params,
                content=body,
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except CircuitOpenException:
            return JSONResponse(
                status_code=503,
                content={"detail": "Circuit Open"},
            )

        except (
            httpx.TimeoutException,
            httpx.HTTPStatusError,
        ):
            return JSONResponse(
                status_code=504,
                content={"detail": "Gateway Timeout"},
            )


proxy = ReverseProxy()
