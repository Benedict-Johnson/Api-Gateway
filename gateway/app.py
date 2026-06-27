from fastapi import FastAPI, HTTPException, Request

from gateway.proxy import proxy
from middleware.auth import AuthenticationMiddleware
from routers.registry import RouteRegistry

app = FastAPI(title="Custom API Gateway")

app.add_middleware(AuthenticationMiddleware)

registry = RouteRegistry("config/routes.yaml")


@app.get("/")
async def root():
    return {"message": "Gateway Running"}


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def gateway(request: Request, path: str):

    full_path = "/" + path

    route = registry.resolve(
        full_path,
        request.method,
    )

    if route is None:
        raise HTTPException(
            status_code=404,
            detail="Route not found"
    )

    service = registry.config.services[route.service].url

    return await proxy.forward(
        request,
        f"{service}{full_path}"
    )