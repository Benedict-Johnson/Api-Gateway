from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from auth.manager import AuthenticationManager
from routing.registry import RouteRegistry


class AuthenticationMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

        self.auth = AuthenticationManager()
        self.registry = RouteRegistry("routing/routes.yaml")

    async def dispatch(self, request: Request, call_next):
        from config.settings import settings

        if settings.DEMO_MODE:
            # TEMPORARY DOCUMENTATION / DEMO MODE: Bypass API key authentication and RBAC checks for all routes
            # (including /docs, /openapi.json, /redoc, /metrics, /health, /live, /ready).
            # Must remain disabled (DEMO_MODE=false) in production environments!
            request.state.user = {"client": "demo-client", "role": "admin"}
            return await call_next(request)

        if request.url.path in ["/", "/health", "/live", "/ready", "/metrics"]:
            return await call_next(request)

        user = await self.auth.authenticate(request)

        if user is None:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        route = self.registry.resolve(request.url.path, request.method)

        if route and route.roles:

            role = user.get("role")

            if role not in route.roles:
                return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        request.state.user = user

        return await call_next(request)
