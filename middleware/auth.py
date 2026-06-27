from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from auth.manager import AuthenticationManager
from routers.registry import RouteRegistry


class AuthenticationMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

        self.auth = AuthenticationManager()
        self.registry = RouteRegistry("config/routes.yaml")

    async def dispatch(self, request: Request, call_next):

        if request.url.path == "/":
            return await call_next(request)

        user = await self.auth.authenticate(request)

        if user is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"}
            )

        route = self.registry.resolve(
            request.url.path,
            request.method
        )

        if route and route.roles:

            role = user.get("role")

            if role not in route.roles:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Forbidden"}
                )

        request.state.user = user

        return await call_next(request)