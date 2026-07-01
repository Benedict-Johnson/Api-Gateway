from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from rate_limiter.config import RateLimitLoader
from rate_limiter.manager import RateLimiterManager


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, config_loader: RateLimitLoader = None):
        super().__init__(app)
        self.config_loader = config_loader or RateLimitLoader("config/rate_limit.yaml")
        self.manager = RateLimiterManager(self.config_loader)

    async def dispatch(self, request: Request, call_next):

        client_ip = request.client.host

        result = await self.manager.allow(client_ip)

        if not result.allowed:
            from observability.logger import logger
            from observability.metrics import GATEWAY_RATE_LIMIT_HITS

            GATEWAY_RATE_LIMIT_HITS.inc()
            logger.warning(f"Rate limit exceeded for IP {client_ip}")

            response = JSONResponse(
                status_code=429, content={"detail": "Rate limit exceeded"}
            )
        else:
            response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Algorithm"] = (
            self.manager.limiter.__class__.__name__
        )

        if result.retry_after is not None:
            response.headers["Retry-After"] = str(result.retry_after)

        return response
