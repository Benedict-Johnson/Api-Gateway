from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from rate_limiter.manager import RateLimiterManager


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.manager = RateLimiterManager()

    async def dispatch(self, request: Request, call_next):

        client_ip = request.client.host

        allowed = await self.manager.allow(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded"
                }
            )

        return await call_next(request)