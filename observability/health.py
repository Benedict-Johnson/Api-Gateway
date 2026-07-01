import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse

START_TIME = time.time()


def create_health_router(redis_client, service_registry, circuit_breaker_policy):
    router = APIRouter(tags=["Health & Readiness"])

    @router.get(
        "/live",
        summary="Liveness Probe",
        description="Kubernetes/Docker liveness probe endpoint. Verifies that the gateway process is running and not deadlocked.",
        responses={
            200: {
                "description": "Gateway process is alive",
                "content": {"application/json": {"example": {"status": "UP"}}},
            }
        },
    )
    async def live():
        return {"status": "UP"}

    @router.get(
        "/ready",
        summary="Readiness Probe",
        description="Kubernetes/Docker readiness probe endpoint. Verifies connectivity to the Redis cluster and confirms that the service registry has loaded upstream destinations.",
        responses={
            200: {
                "description": "Gateway is ready to accept traffic",
                "content": {"application/json": {"example": {"status": "UP"}}},
            },
            503: {
                "description": "Gateway not ready - Redis unreachable or empty registry",
                "content": {
                    "application/json": {
                        "example": {"status": "DOWN", "reason": "Redis ping failed"}
                    }
                },
            },
        },
    )
    async def ready():
        # Check Redis connection
        try:
            is_ready = await redis_client.ping()
            if not is_ready:
                return JSONResponse(
                    status_code=503,
                    content={"status": "DOWN", "reason": "Redis ping failed"},
                )
        except Exception:
            return JSONResponse(
                status_code=503,
                content={"status": "DOWN", "reason": "Redis connection error"},
            )

        # Check Service Registry
        if not service_registry.services:
            return JSONResponse(
                status_code=503,
                content={"status": "DOWN", "reason": "Service registry empty"},
            )

        return {"status": "UP"}

    @router.get(
        "/health",
        summary="Comprehensive System Health Check",
        description="Returns detailed health diagnostics including Redis cache connectivity status, registered upstream microservices status, individual circuit breaker states (CLOSED/OPEN/HALF_OPEN), and total gateway uptime in seconds.",
        responses={
            200: {
                "description": "Detailed health report",
                "content": {
                    "application/json": {
                        "example": {
                            "gateway": "UP",
                            "redis": "UP",
                            "cache": "UP",
                            "registered_services": {"user-service": "UP"},
                            "circuit_breakers": {"user-service": "closed"},
                            "uptime_seconds": 3600,
                        }
                    }
                },
            }
        },
    )
    async def health():
        redis_status = "UP"
        try:
            if not await redis_client.ping():
                redis_status = "DOWN"
        except Exception:
            redis_status = "DOWN"

        registered_services = {}
        circuit_breakers = {}

        for service_name, service in service_registry.services.items():
            # If a service has active instances, we consider it UP for this snapshot
            is_up = any(inst for inst in service.instances)
            registered_services[service_name] = "UP" if is_up else "DOWN"

            # Fetch Circuit breaker state safely
            breaker = await circuit_breaker_policy.get_breaker(service_name)
            cb_state = await breaker.get_state()
            circuit_breakers[service_name] = cb_state.value

        return {
            "gateway": "UP",
            "redis": redis_status,
            "cache": redis_status,  # Using same Redis cluster for now
            "registered_services": registered_services,
            "circuit_breakers": circuit_breakers,
            "uptime_seconds": int(time.time() - START_TIME),
        }

    return router
