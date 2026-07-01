from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that automatically injects configurable security headers into all HTTP responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if settings.SECURITY_HEADERS_ENABLED:
            if settings.HSTS_HEADER:
                response.headers["Strict-Transport-Security"] = settings.HSTS_HEADER
            if settings.X_FRAME_OPTIONS_HEADER:
                response.headers["X-Frame-Options"] = settings.X_FRAME_OPTIONS_HEADER
            if settings.X_CONTENT_TYPE_OPTIONS_HEADER:
                response.headers["X-Content-Type-Options"] = (
                    settings.X_CONTENT_TYPE_OPTIONS_HEADER
                )
            if settings.REFERRER_POLICY_HEADER:
                response.headers["Referrer-Policy"] = settings.REFERRER_POLICY_HEADER
            if settings.PERMISSIONS_POLICY_HEADER:
                response.headers["Permissions-Policy"] = (
                    settings.PERMISSIONS_POLICY_HEADER
                )
            if settings.CONTENT_SECURITY_POLICY_HEADER:
                response.headers["Content-Security-Policy"] = (
                    settings.CONTENT_SECURITY_POLICY_HEADER
                )

        return response
