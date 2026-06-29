from fastapi import FastAPI, HTTPException, Request

from gateway.proxy import proxy
from cache.middleware import CacheMiddleware
from auth.middleware import AuthenticationMiddleware
from rate_limiter.middleware import RateLimitMiddleware
from observability.middleware import ObservabilityMiddleware

from routing.registry import RouteRegistry
from load_balancer.discovery.router import router as discovery_router
from load_balancer.registry import ServiceRegistry
from load_balancer.manager import LoadBalancerManager
import asyncio
from load_balancer.discovery.cleanup import (
    cleanup_manager,
)

from prometheus_client import make_asgi_app
from observability.health import create_health_router
from cache.redis import cache_redis
from observability.context import service_name_var
from observability.logger import logger
from config.validator import validate_all

validate_all()

app = FastAPI(title="Custom API Gateway")

registry = RouteRegistry("routing/routes.yaml")
service_registry = ServiceRegistry("load_balancer/services.yaml")
load_balancer = LoadBalancerManager()

app.include_router(discovery_router)

# Mount health endpoints
health_router = create_health_router(cache_redis.client, service_registry, proxy.resilience_manager.circuit_breaker)
app.include_router(health_router)

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Mount metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Middlewares are executed bottom-up in Starlette!
app.add_middleware(CacheMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(ObservabilityMiddleware)


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
        
    service_name_var.set(route.service)

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
            f"{instance.url}{full_path}",
            route.service,
        )

    finally:

        instance.active_connections -= 1

    return response

@app.on_event("startup")
async def startup():

    asyncio.create_task(
        cleanup_manager.run()
    )

from gateway.lifecycle import lifecycle_manager

@app.on_event("shutdown")
async def shutdown_event():
    await lifecycle_manager.trigger_shutdown()