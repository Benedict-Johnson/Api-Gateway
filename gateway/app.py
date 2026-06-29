from fastapi import FastAPI, HTTPException, Request

from gateway.proxy import proxy

from auth.middleware import AuthenticationMiddleware
from rate_limiter.middleware import RateLimitMiddleware

from routing.registry import RouteRegistry

from load_balancer.registry import ServiceRegistry
from load_balancer.manager import LoadBalancerManager


app = FastAPI(title="Custom API Gateway")

app.add_middleware(AuthenticationMiddleware)
app.add_middleware(RateLimitMiddleware)


registry = RouteRegistry("routing/routes.yaml")

service_registry = ServiceRegistry(
    "load_balancer/services.yaml"
)

load_balancer = LoadBalancerManager()


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

    service = service_registry.get(route.service)

    if service is None:
        raise HTTPException(
            status_code=500,
            detail="Unknown service"
        )

    instance = load_balancer.next(service)

    instance.active_connections += 1

    try:

        response = await proxy.forward(
            request,
            f"{instance.url}{full_path}"
        )

    finally:

        instance.active_connections -= 1

    return response