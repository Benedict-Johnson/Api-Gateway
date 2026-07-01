import asyncio

from fastapi import FastAPI, HTTPException, Request

from auth.admin_router import router as admin_router
from auth.middleware import AuthenticationMiddleware
from cache.middleware import CacheMiddleware
from cache.redis import cache_redis
from config.validator import validate_all
from database.database import init_db
from gateway.proxy import proxy
from gateway.request_validation import RequestValidationMiddleware
from gateway.security_headers import SecurityHeadersMiddleware
from load_balancer.discovery.cleanup import (
    cleanup_manager,
)
from load_balancer.discovery.router import router as discovery_router
from load_balancer.manager import LoadBalancerManager
from load_balancer.registry import ServiceRegistry
from observability.context import service_name_var
from observability.health import create_health_router
from observability.middleware import ObservabilityMiddleware
from rate_limiter.middleware import RateLimitMiddleware
from routing.registry import RouteRegistry

validate_all()
init_db()

app = FastAPI(
    title="Custom API Gateway",
    description="An enterprise-grade, high-performance asynchronous API Gateway built with FastAPI, Redis, and PostgreSQL. Features reverse proxying, dynamic load balancing, service discovery, distributed caching, rate limiting, circuit breaking, retry/timeout resilience, RBAC authentication, and comprehensive observability.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Health & Readiness",
            "description": "Endpoints for liveness, readiness, and full system health checks.",
        },
        {
            "name": "Observability",
            "description": "Prometheus metrics export and system telemetry.",
        },
        {
            "name": "Service Discovery",
            "description": "Dynamic service registration and heartbeat monitoring.",
        },
        {
            "name": "Administration",
            "description": "RBAC-protected administrative operations for API key management.",
        },
        {
            "name": "Gateway Proxy",
            "description": "Reverse proxy routing to upstream backend microservices.",
        },
    ],
)

registry = RouteRegistry("routing/routes.yaml")
service_registry = ServiceRegistry("load_balancer/services.yaml")
load_balancer = LoadBalancerManager()

app.include_router(discovery_router)
app.include_router(admin_router)

# Mount health endpoints
health_router = create_health_router(
    cache_redis.client, service_registry, proxy.resilience_manager.circuit_breaker
)
app.include_router(health_router)

from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


# Mount metrics endpoint
@app.get(
    "/metrics",
    tags=["Observability"],
    summary="Prometheus Metrics",
    description="Returns real-time gateway performance metrics, request counters, latency histograms, and rate limit telemetry formatted for Prometheus scraping.",
    responses={
        200: {
            "description": "Prometheus plaintext metrics",
            "content": {
                "text/plain; version=0.0.4; charset=utf-8": {
                    "example": '# HELP gateway_requests_total Total requests\n# TYPE gateway_requests_total counter\ngateway_requests_total{method="GET",path="/users",status="200"} 42.0\n'
                }
            },
        },
        500: {"description": "Internal Server Error"},
    },
)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Middlewares are executed bottom-up in Starlette!
app.add_middleware(CacheMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ObservabilityMiddleware)


@app.get(
    "/",
    tags=["Health & Readiness"],
    summary="Gateway Root Status",
    description="Returns a basic status check confirming that the API Gateway process is active and running.",
    responses={
        200: {
            "description": "Gateway online confirmation",
            "content": {
                "application/json": {"example": {"message": "Gateway Running"}}
            },
        }
    },
)
async def root():
    return {"message": "Gateway Running"}


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    tags=["Gateway Proxy"],
    summary="Reverse Proxy Route Handler",
    description="Dynamically resolves incoming request paths against configured routes, applies load balancing (least-connections/round-robin/weighted), enforces rate limits and authentication, checks distributed cache, and forwards requests to upstream backend microservices with circuit breaker and retry resilience.",
    responses={
        200: {"description": "Successful upstream response forwarded to client"},
        400: {
            "description": "Bad Request - Malformed payload or validation error",
            "content": {
                "application/json": {"example": {"detail": "Malformed JSON payload"}}
            },
        },
        401: {
            "description": "Unauthorized - Missing or invalid API Key / JWT Token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or missing API key"}
                }
            },
        },
        403: {
            "description": "Forbidden - Insufficient permissions / RBAC violation",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient permissions for this endpoint"}
                }
            },
        },
        404: {
            "description": "Not Found - Route or resource not found",
            "content": {"application/json": {"example": {"detail": "Route not found"}}},
        },
        413: {
            "description": "Payload Too Large - Request body exceeds limit",
            "content": {
                "application/json": {
                    "example": {"detail": "Payload size exceeds configured limit"}
                }
            },
        },
        414: {
            "description": "URI Too Long - Request URI exceeds limit",
            "content": {
                "application/json": {
                    "example": {"detail": "URI length exceeds configured limit"}
                }
            },
        },
        415: {
            "description": "Unsupported Media Type - Content-Type not permitted",
            "content": {
                "application/json": {"example": {"detail": "Unsupported content type"}}
            },
        },
        429: {
            "description": "Too Many Requests - Rate limit exceeded",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded"}}
            },
        },
        431: {
            "description": "Request Header Fields Too Large",
            "content": {
                "application/json": {
                    "example": {"detail": "Header size exceeds configured limit"}
                }
            },
        },
        500: {
            "description": "Internal Server Error - Gateway or service failure",
            "content": {"application/json": {"example": {"detail": "Unknown service"}}},
        },
        502: {
            "description": "Bad Gateway - Upstream service unreachable or circuit open",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Circuit breaker is open for service: user-service"
                    }
                }
            },
        },
        503: {"description": "Service Unavailable - No healthy instances available"},
        504: {
            "description": "Gateway Timeout - Upstream service timed out",
            "content": {
                "application/json": {"example": {"detail": "Upstream request timeout"}}
            },
        },
    },
)
async def gateway(request: Request, path: str):

    full_path = "/" + path

    route = registry.resolve(
        full_path,
        request.method,
    )

    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")

    service_name_var.set(route.service)

    service = service_registry.get(route.service)

    if service is None:
        raise HTTPException(status_code=500, detail="Unknown service")

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

    asyncio.create_task(cleanup_manager.run())


from gateway.lifecycle import lifecycle_manager


@app.on_event("shutdown")
async def shutdown_event():
    await lifecycle_manager.trigger_shutdown()
